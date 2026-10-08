import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

with (PROJECT_ROOT / "app.js").open("r", encoding="utf-8") as f:
    content = f.read()

# Parse the accounts list accurately using AST/regex handling of escaped quotes
lines = content.splitlines()
existing_accounts = []
in_accounts = False
for line in lines:
    if "accounts: [" in line:
        in_accounts = True
        continue
    if in_accounts and line.strip() == "],":
        in_accounts = False
        break
    if in_accounts:
        # Match code, label, type, parent, etc.
        m = re.search(r"code:\s*'([^']+)'\s*,\s*label:\s*'((?:\\'|[^'])*)'", line)
        if m:
            c = m.group(1)
            l = m.group(2).replace(r"\'", "'")
            existing_accounts.append({"code": c, "label": l, "line": line.strip()})

with (DATA_DIR / "existing_accounts_clean.json").open("w", encoding="utf-8") as f:
    json.dump(existing_accounts, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(existing_accounts)} existing accounts accurately.")

