let fuse = null;
let searchIndex = null;

async function loadSearchIndex() {
  if (searchIndex) return;
  const res = await fetch('/index.json');
  searchIndex = await res.json();
  fuse = new Fuse(searchIndex, {
    keys: [
      { name: 'headline', weight: 0.35 },
      { name: 'title', weight: 0.2 },
      { name: 'summary', weight: 0.2 },
      { name: 'content', weight: 0.1 },
      { name: 'era', weight: 0.1 },
      { name: 'historydate', weight: 0.05 }
    ],
    threshold: 0.35,
    includeScore: true,
    includeMatches: true,
    minMatchCharLength: 2
  });
}

function openSearch() {
  const overlay = document.getElementById('searchOverlay');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
  loadSearchIndex().then(function() {
    document.getElementById('searchInput').focus();
  });
}

function closeSearch() {
  const overlay = document.getElementById('searchOverlay');
  overlay.classList.remove('active');
  document.body.style.overflow = '';
  document.getElementById('searchInput').value = '';
  document.getElementById('searchResults').innerHTML = '';
}

function renderResults(results) {
  const container = document.getElementById('searchResults');

  if (results.length === 0) {
    container.innerHTML = '<p class="search-no-results">No articles found. Try a different keyword.</p>';
    return;
  }

  let html = '';
  results.forEach(function(r) {
    const item = r.item;
    html += '<a href="' + item.url + '" class="search-result-card">'
      + '<div class="search-result-img" style="background-image:url(\'' + item.image + '\')"></div>'
      + '<div class="search-result-body">'
      + '<span class="search-result-era">' + (item.era || '') + '</span>'
      + '<h3 class="search-result-headline">' + item.headline + '</h3>'
      + '<p class="search-result-summary">' + item.summary + '</p>'
      + '<span class="search-result-date">' + (item.historydate || '') + '</span>'
      + '</div></a>';
  });

  container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
  // Toggle buttons
  document.querySelectorAll('.search-toggle').forEach(function(btn) {
    btn.addEventListener('click', openSearch);
  });
  document.getElementById('searchClose').addEventListener('click', closeSearch);

  // Close on overlay background click
  document.getElementById('searchOverlay').addEventListener('click', function(e) {
    if (e.target === this) closeSearch();
  });

  // Close on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSearch();
    // Ctrl/Cmd + K to open search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearch();
    }
  });

  // Live search on input
  let debounce = null;
  document.getElementById('searchInput').addEventListener('input', function() {
    const query = this.value.trim();
    clearTimeout(debounce);

    if (query.length < 2) {
      document.getElementById('searchResults').innerHTML = '';
      return;
    }

    debounce = setTimeout(function() {
      if (!fuse) return;
      const results = fuse.search(query, { limit: 10 });
      renderResults(results);
    }, 150);
  });
});
