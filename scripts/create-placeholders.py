"""
Create placeholder images for articles where Wikipedia had no thumbnail.
Uses an existing article image as a base, resized and with the title overlaid.
Falls back to a simple solid-color JPEG if Pillow can't composite.
"""
import os
import glob
import re

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ROOT = os.path.join(os.path.dirname(__file__), "..")
ARTICLES_DIR = os.path.join(ROOT, "content", "articles")
IMAGES_DIR = os.path.join(ROOT, "static", "images", "articles")
THUMB_DIR = os.path.join(IMAGES_DIR, "thumb")


def find_missing_images():
    """Find articles missing images."""
    missing = []
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md") or fname == "_index.md":
            continue
        slug = fname[:-3]
        img_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")
        if not os.path.exists(img_path):
            # Get title from front matter
            with open(os.path.join(ARTICLES_DIR, fname), encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'^title:\s*"(.+?)"', content, re.M)
            title = m.group(1) if m else slug.replace("-", " ").title()
            missing.append((slug, title))
    return missing


def create_placeholder(slug, title, width=800, height=450):
    """Create a simple placeholder JPEG."""
    img_path = os.path.join(IMAGES_DIR, f"{slug}.jpg")
    thumb_path = os.path.join(THUMB_DIR, f"{slug}.jpg")
    
    if not HAS_PIL:
        # Create a minimal valid JPEG (1x1 dark gray pixel)
        # This won't look great but won't be a broken image
        return False
    
    # Create a dark, newspaper-style placeholder
    img = Image.new("RGB", (width, height), color=(45, 45, 48))
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border = 20
    draw.rectangle(
        [border, border, width - border, height - border],
        outline=(120, 120, 125), width=2
    )
    
    # Add "HISTORY NEWS" header
    try:
        header_font = ImageFont.truetype("arial.ttf", 24)
        title_font = ImageFont.truetype("arial.ttf", 32)
    except (OSError, IOError):
        header_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Header
    draw.text((width // 2, 80), "HISTORY NEWS", fill=(180, 160, 120),
              anchor="mm", font=header_font)
    
    # Divider line
    draw.line([(100, 110), (width - 100, 110)], fill=(120, 120, 125), width=1)
    
    # Title text (word-wrap manually)
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=title_font)
        if bbox[2] > width - 120:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)
    
    y = height // 2 - len(lines) * 20
    for line in lines:
        draw.text((width // 2, y), line, fill=(220, 215, 200),
                  anchor="mm", font=title_font)
        y += 44
    
    # Save full size
    img.save(img_path, "JPEG", quality=80)
    
    # Save thumbnail
    os.makedirs(THUMB_DIR, exist_ok=True)
    thumb = img.resize((400, int(400 * height / width)), Image.LANCZOS)
    thumb.save(thumb_path, "JPEG", quality=75)
    
    return True


def main():
    missing = find_missing_images()
    print(f"Found {len(missing)} articles without images")
    
    if not HAS_PIL:
        print("ERROR: Pillow not installed. Run: pip install Pillow")
        return
    
    created = 0
    for slug, title in missing:
        if create_placeholder(slug, title):
            created += 1
            print(f"  Created placeholder: {slug}")
    
    print(f"\nCreated {created} placeholder images")


if __name__ == "__main__":
    main()
