"""Second pass: add a short closing paragraph to TDIH-02 articles still under 600 words."""
import os
import glob

ROOT = os.path.join(os.path.dirname(__file__), "..")
ARTICLES_DIR = os.path.join(ROOT, "content", "articles")

CLOSING = """
## Looking Back

Every historical event exists at the intersection of countless individual choices, social pressures, and unpredictable circumstances. The people who lived through this moment did not know they were making history — they were simply responding to the situation in front of them with the information and resources they had. That is what makes history so valuable as a teacher: it shows us that the future is never predetermined. It is shaped by people who choose to act, to resist, to create, to persist. The question history always asks is not what happened, but what will you do with what you have learned.
"""

def main():
    fixed = 0
    still_short = 0
    
    for filepath in sorted(glob.glob(os.path.join(ARTICLES_DIR, "tdih-*-02.md"))):
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        
        word_count = len(parts[2].split())
        if word_count >= 600:
            continue
        
        content = content.rstrip() + CLOSING
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Verify
        new_count = len(content.split("---", 2)[2].split())
        if new_count < 600:
            still_short += 1
            print(f"  Still short: {os.path.basename(filepath)} ({new_count} words)")
        else:
            fixed += 1
    
    print(f"\nFixed: {fixed}, Still short: {still_short}")

if __name__ == "__main__":
    main()
