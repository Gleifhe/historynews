# Fix memorial-day template to use thumbnails
from pathlib import Path
p = Path(__file__).parent.parent / 'layouts' / 'memorial-day' / 'single.html'
content = p.read_text(encoding='utf-8')
old = """style="background-image: url('{{ .Params.image }}')" """
new = """style="background-image: url('{{ replace .Params.image "/images/articles/" "/images/articles/thumb/" }}')" """
count = content.count(old.strip())
content = content.replace(old.strip(), new.strip())
p.write_text(content, encoding='utf-8')
print(f'Fixed {count} card images in memorial-day/single.html')
