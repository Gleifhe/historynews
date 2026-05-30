"""Quick stats for documentation updates."""
import glob, re, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

files = [f for f in glob.glob("content/articles/*.md") if not f.endswith("_index.md")]
print(f"Total articles: {len(files)}")

tdih = [f for f in files if os.path.basename(f).startswith("tdih-")]
print(f"TDIH articles: {len(tdih)}")
print(f"Non-TDIH articles: {len(files) - len(tdih)}")

eras = set()
for f in files:
    with open(f, encoding="utf-8") as fh:
        m = re.search(r'^era:\s*"(.+?)"', fh.read(), re.M)
        if m:
            eras.add(m.group(1))

print(f"\nUnique eras: {len(eras)}")
for e in sorted(eras):
    print(f"  {e}")

scripts = glob.glob("scripts/*.py") + glob.glob("scripts/*.ps1")
print(f"\nScripts: {len(scripts)} ({len(glob.glob('scripts/*.py'))} Python + {len(glob.glob('scripts/*.ps1'))} PowerShell)")
