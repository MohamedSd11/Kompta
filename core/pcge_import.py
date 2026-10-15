"""Source-backed import of the general-business chart from the official CGNC dataset.

`cgnc_standard_accounts.json` (plus the documented supplement) is the source of
labels and codes. It covers classes 1-8; classes 0 and 9 are special/analytical
accounts and stay outside this import. Dataset entries whose status is
`needs_review` are reported for review instead of being imported.
"""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
from typing import Any

from .cgnc import STANDARD_DATASET, chart_of_accounts, read_dataset
from .storage import connect_database, utc_now_iso

PCGE_CLASS_LABELS = {
    1: "FINANCEMENT PERMANENT",
    2: "ACTIF IMMOBILISÉ",
    3: "ACTIF CIRCULANT (HORS TRÉSORERIE)",
    4: "PASSIF CIRCULANT (HORS TRÉSORERIE)",
    5: "TRÉSORERIE",
    6: "CHARGES",
    7: "PRODUITS",
    8: "RÉSULTATS",
}
HIERARCHY_LEVELS = {2: "rubrique", 3: "poste", 4: "principal", 5: "divisionnaire"}


def resolve_pcge_source(path: str | Path | None = None) -> Path:
    source = Path(path or STANDARD_DATASET).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"CGNC source dataset not found: {source}")
    return source


def extract_pcge_general_accounts(path: str | Path | None = None) -> list[dict[str, Any]]:
    resolve_pcge_source(path)
    records = read_dataset(path, "cgnc_standard") if path else list(chart_of_accounts())
    accounts = []
    for record in records:
        account = {"code": record["code"], "label": record["label"], "class": record["class"], "source": record["source"]}
        if record["status"] == "needs_review":
            account["needs_review"] = True
            account["review_reason"] = "cgnc_dataset_status"
        accounts.append(account)
    return sorted(accounts, key=lambda item: (item["class"], item["code"]))


def account_parent(code: str, codes: set[str]) -> str | None:
    parents = [candidate for candidate in codes if candidate != code and code.startswith(candidate)]
    return max(parents, key=len) if parents else None


def preview_import(existing: list[dict[str, Any]], source_path: str | Path | None = None) -> dict[str, Any]:
    source_accounts = extract_pcge_general_accounts(source_path)
    existing_by_code = {str(item.get("code", "")).strip(): item for item in existing if item.get("code")}
    source_codes = {item["code"] for item in source_accounts}
    added, present, review = [], [], []
    for account in source_accounts:
        current = existing_by_code.get(account["code"])
        if account.get("needs_review"):
            review.append(account)
        elif current:
            present.append({"code": account["code"], "sourceLabel": account["label"], "currentLabel": current.get("label") or current.get("libelle", "")})
        else:
            added.append({**account, "parent": account_parent(account["code"], source_codes)})
    return {
        "source": str(resolve_pcge_source(source_path)),
        "scope": "general_business_classes_1_to_8",
        "sourceCount": len(source_accounts),
        "added": added,
        "alreadyPresent": present,
        "needsReview": review,
        "excludedClasses": [0, 9],
    }


def seed_catalog_if_empty(database: str | Path | None = None) -> int:
    """Fill an empty `pcm_accounts` from the bundled CGNC dataset; returns rows inserted."""
    accounts = [a for a in chart_of_accounts() if len(a["code"]) in HIERARCHY_LEVELS]
    codes = {a["code"] for a in accounts}
    now = utc_now_iso()
    records = [
        (str(number), label, None, "parent", "class", "cgnc_dataset", now)
        for number, label in PCGE_CLASS_LABELS.items()
    ]
    for account in accounts:
        code = account["code"]
        parent = max((c for c in codes if c != code and code.startswith(c)), key=len, default=code[0])
        kind = "parent" if any(c != code and c.startswith(code) for c in codes) else "account"
        records.append((code, account["label"], parent, kind, HIERARCHY_LEVELS[len(code)], "cgnc_dataset", now))

    with closing(connect_database(database, autocommit=True)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            if db.execute("SELECT EXISTS(SELECT 1 FROM pcm_accounts)").fetchone()[0]:
                db.execute("ROLLBACK")
                return 0
            db.executemany(
                "INSERT INTO pcm_accounts(code, label, parent, account_type, hierarchy_level, catalog_source, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                records,
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
    return len(records)
