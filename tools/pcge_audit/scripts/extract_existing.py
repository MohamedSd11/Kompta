import re
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

with (PROJECT_ROOT / "app.js").open("r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
accounts = []
for line in lines:
    m = re.search(r"\{\s*code:\s*['\"]([^'\"]+)['\"],\s*label:\s*['\"]([^'\"]+)['\"]", line)
    if m:
        accounts.append({"code": m.group(1), "label": m.group(2)})

print(f"Total accounts found in app.js: {len(accounts)}")
with (DATA_DIR / "existing_accounts.json").open("w", encoding="utf-8") as f:
    json.dump(accounts, f, ensure_ascii=False, indent=2)

