import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

with (DATA_DIR / "existing_accounts_clean.json").open("r", encoding="utf-8") as f:
    existing = json.load(f)

with (DATA_DIR / "official_plan_cgnc.json").open("r", encoding="utf-8") as f:
    official = json.load(f)

def clean_txt(s):
    if not s:
        return ""
    s = s.lower().strip()
    # Normalize accents
    for a, b in [("é","e"), ("è","e"), ("ê","e"), ("ë","e"), ("à","a"), ("â","a"), ("î","i"), ("ï","i"), ("ô","o"), ("ù","u"), ("û","u"), ("ç","c")]:
        s = s.replace(a, b)
    s = re.sub(r"[\'’\"«»\.,\(\)\-\–—/]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

existing_map = {}
for e in existing:
    c = e["code"]
    if c not in existing_map:
        existing_map[c] = []
    existing_map[c].append(e["label"])

already_present = []
missing = []
needs_review = []

for off in official:
    c = off["code"]
    l_off = off["label"]
    page = off["printed_page"]
    classe = off["classe"]

    if c in existing_map:
        kompta_labels = existing_map[c]
        # check match
        is_match = False
        for kl in kompta_labels:
            if clean_txt(kl) == clean_txt(l_off):
                is_match = True
                already_present.append({
                    "code": c,
                    "official_label": l_off,
                    "kompta_label": kl,
                    "printed_page": page,
                    "classe": classe
                })
                break
        if not is_match:
            # Different label
            needs_review.append({
                "code": c,
                "official_label": l_off,
                "kompta_label": " | ".join(kompta_labels),
                "printed_page": page,
                "classe": classe
            })
    else:
        missing.append({
            "code": c,
            "official_label": l_off,
            "printed_page": page,
            "classe": classe
        })

print(f"Total Official: {len(official)}")
print(f"Already Present (exact / standard accent match): {len(already_present)}")
print(f"Needs Review (code exists, label difference): {len(needs_review)}")
print(f"Missing (not in Kompta): {len(missing)}")

with (DATA_DIR / "audit_categorized.json").open("w", encoding="utf-8") as f:
    json.dump({
        "already_present": already_present,
        "needs_review": needs_review,
        "missing": missing
    }, f, ensure_ascii=False, indent=2)

