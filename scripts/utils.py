"""
utils.py — Shared utility module for History News scripts.

Provides common functions used across the automation pipeline:
- Front matter parsing (YAML)
- Article file iteration
- Body text extraction
- URL checking with HEAD/GET fallback
- Wikipedia API wrapper with batching, maxlag, Retry-After
- Slug-to-Wikipedia manifest loading
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
ARTICLES_DIR = ROOT / 'content' / 'articles'
IMAGES_DIR = ROOT / 'static' / 'images' / 'articles'
MANIFEST_PATH = ROOT / 'scripts' / 'slug-to-wiki.json'
CONFIG_PATH = ROOT / 'config.toml'

USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'

# Use default SSL context (verifies certificates)
SSL_CTX = ssl.create_default_context()


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def get_base_url():
    """Read baseURL from config.toml."""
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text(encoding='utf-8').splitlines():
            m = re.match(r'baseURL\s*=\s*"([^"]+)"', line)
            if m:
                return m.group(1).rstrip('/')
    return 'https://red-stone-0ed2b5d10.7.azurestaticapps.net'


# ---------------------------------------------------------------------------
# Article helpers
# ---------------------------------------------------------------------------

def get_article_files(directory=None, exclude_index=True):
    """Yield sorted .md article files from the articles directory."""
    d = directory or ARTICLES_DIR
    for f in sorted(d.iterdir()):
        if not f.name.endswith('.md'):
            continue
        if exclude_index and f.name == '_index.md':
            continue
        yield f


def parse_front_matter(content):
    """Parse YAML front matter from Hugo markdown content.

    Returns (dict, body_text). Uses regex parsing that handles the
    double-quoted YAML format used in this project.
    """
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    fm_text = parts[1]
    body = parts[2]

    fm = {}
    # Parse simple key: "value" fields
    for m in re.finditer(r'^(\w+):\s*"((?:[^"\\]|\\.)*)"\s*$', fm_text, re.MULTILINE):
        fm[m.group(1)] = m.group(2).replace('\\"', '"')

    # Parse unquoted fields (weight, draft, etc.)
    for m in re.finditer(r'^(\w+):\s*([^"\n][^\n]*?)\s*$', fm_text, re.MULTILINE):
        key = m.group(1)
        if key not in fm:
            fm[key] = m.group(2)

    # Parse sources list
    sources = re.findall(r'^\s+-\s*"((?:[^"\\]|\\.)*)"\s*$', fm_text, re.MULTILINE)
    if sources:
        fm['sources'] = [s.replace('\\"', '"') for s in sources]

    fm['_raw'] = fm_text
    return fm, body


def extract_body(content):
    """Extract the body text (after front matter) from Hugo markdown."""
    parts = content.split('---', 2)
    return parts[2] if len(parts) >= 3 else content


def extract_front_matter_raw(content):
    """Extract the raw front matter text between --- delimiters."""
    parts = content.split('---', 2)
    return parts[1] if len(parts) >= 3 else ''


# ---------------------------------------------------------------------------
# URL checking
# ---------------------------------------------------------------------------

def check_url(url, timeout=10):
    """Check if a URL is reachable via HEAD, falling back to GET.

    Returns (status, detail) where status is 'OK', 'ERROR', 'TIMEOUT', or 'REDIRECT'.
    """
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            code = resp.getcode()
            final_url = resp.geturl()
            if final_url != url:
                return 'REDIRECT', f'{code} -> {final_url[:80]}'
            return 'OK', code
    except urllib.error.HTTPError as e:
        if e.code in (405, 403):
            # Some sites block HEAD, try GET with delay
            time.sleep(1)
            req2 = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req2, timeout=timeout, context=SSL_CTX) as resp:
                    return 'OK', resp.getcode()
            except Exception:
                return 'OK', '403/405 likely valid'
        return 'ERROR', e.code
    except urllib.error.URLError as e:
        return 'ERROR', str(e.reason)[:40]
    except TimeoutError:
        return 'TIMEOUT', timeout
    except (OSError, ValueError) as e:
        return 'ERROR', str(e)[:40]


# ---------------------------------------------------------------------------
# Wikipedia API
# ---------------------------------------------------------------------------

def load_slug_to_wiki():
    """Load slug-to-Wikipedia-title mapping from the JSON manifest."""
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    return {}


def wiki_api_request(params):
    """Make a Wikipedia API request with maxlag, retries, and Retry-After.

    Returns parsed JSON or None on failure.
    """
    base_url = 'https://en.wikipedia.org/w/api.php'
    params['format'] = 'json'
    params['maxlag'] = '5'
    url = f'{base_url}?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                retry_after = e.headers.get('Retry-After', '')
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 10 * (attempt + 1)
                print(f'  Rate limited ({e.code}), waiting {wait}s...')
                time.sleep(wait)
                continue
            return None
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def wiki_batch_query(titles, prop='extracts', extra_params=None):
    """Query Wikipedia API in batches of 50 titles.

    Args:
        titles: list of Wikipedia article titles
        prop: property to fetch (e.g. 'extracts', 'pageimages|imageinfo')
        extra_params: dict of additional API parameters

    Returns:
        dict mapping title -> page data
    """
    results = {}
    title_list = list(set(titles))
    base_params = {
        'action': 'query',
        'prop': prop,
        'redirects': '1',
    }
    if extra_params:
        base_params.update(extra_params)

    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        params = dict(base_params)
        params['titles'] = '|'.join(batch)

        data = wiki_api_request(params)
        if data and 'query' in data and 'pages' in data['query']:
            # Build normalized/redirect lookup for title resolution
            title_map = {}
            for n in data['query'].get('normalized', []):
                title_map[n['from']] = n['to']
            for r in data['query'].get('redirects', []):
                title_map[r['from']] = r['to']

            for page_id, page in data['query']['pages'].items():
                if page_id != '-1':
                    results[page.get('title', '')] = page

        if i + 50 < len(title_list):
            time.sleep(5)

    return results


def download_image(url, dest_path, timeout=15):
    """Download an image from a URL to a local path.

    Returns True on success, False on failure.
    """
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            data = resp.read()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        return True
    except Exception as e:
        print(f'  Download failed: {e}')
        return False
