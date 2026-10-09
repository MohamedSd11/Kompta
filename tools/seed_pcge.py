"""Extract the supplied PCGE PDF and replace the database's class 1–8 catalog."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "cgnc_standard_accounts.json"
ACCOUNT_LINE = re.compile(r"^\s*(\d{2,5})\s+(.+?)\s*$")
CLASS_LINE = re.compile(r"^\s*CLASSE\s+([1-8])(?:\s*\([^)]*\))?\s*:\s*(.*?)\s*$", re.IGNORECASE)
HIERARCHY_LEVELS = {
    1: "class",
    2: "rubrique",
    3: "poste",
    4: "principal",
    5: "divisionnaire",
}
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
PCM_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS pcm_accounts (
        code TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        parent TEXT,
        account_type TEXT NOT NULL DEFAULT 'parent',
        hierarchy_level TEXT NOT NULL DEFAULT 'account',
        catalog_source TEXT NOT NULL DEFAULT 'existing',
        updated_at TEXT NOT NULL
    )
"""


def parse_pcge_page(text: str, page_number: int) -> list[dict[str, Any]]:
    """Extract account rows from one PDF page, excluding headings and page furniture."""
    accounts = []
    for line in text.splitlines():
        match = ACCOUNT_LINE.fullmatch(line)
        if not match:
            continue
        code, label = match.groups()
        label = label.strip().removeprefix("-").strip()
        if code[0] not in "12345678" or not label:
            continue
        accounts.append({
            "account_code": code,
            "label_fr": label,
            "class": int(code[0]),
            "page_pdf": page_number,
            "status": "standard",
        })
    return accounts


def extract_pcge_accounts(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Extract and validate the complete account list for classes 1 through 8."""
    path = Path(pdf_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"PCGE PDF not found: {path}")

    accounts = []
    class_labels: dict[int, str] = {}
    for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
        text = page.extract_text() or ""
        for line in text.splitlines():
            heading = CLASS_LINE.fullmatch(line)
            if heading:
                class_number = int(heading.group(1))
                class_labels[class_number] = PCGE_CLASS_LABELS[class_number]
        accounts.extend(parse_pcge_page(text, page_number))

    codes = [account["account_code"] for account in accounts]
    duplicates = sorted({code for code in codes if codes.count(code) > 1})
    classes = {account["class"] for account in accounts}
    if duplicates:
        raise ValueError(f"Duplicate PCGE account codes: {', '.join(duplicates)}")
    if classes != set(range(1, 9)):
        raise ValueError(f"PCGE source must contain classes 1–8; found {sorted(classes)}")
    if any("\ufffd" in account["label_fr"] for account in accounts):
        raise ValueError("PCGE PDF text contains undecodable account labels")
    if set(class_labels) != set(range(1, 9)):
        raise ValueError(f"PCGE source must contain all class headings; found {sorted(class_labels)}")
    codes = {account["account_code"] for account in accounts}
    for account in accounts:
        code = account["account_code"]
        candidate_parents = (
            candidate for candidate in codes
            if candidate != code and code.startswith(candidate)
        )
        account["parent_code"] = max(candidate_parents, key=len, default=code[0])
        account["hierarchy_level"] = HIERARCHY_LEVELS[len(code)]
        account["class_label"] = class_labels[account["class"]]
    return sorted(accounts, key=lambda account: (account["class"], account["account_code"]))


def _database_records(accounts: list[dict[str, Any]]) -> list[tuple[str, str, str | None, str, str, str]]:
    codes = {account["account_code"] for account in accounts}
    records = [
        (str(class_number), PCGE_CLASS_LABELS[class_number], None, "parent", "class", "pcge_pdf")
        for class_number in range(1, 9)
    ]
    for account in accounts:
        code = account["account_code"]
        parents = (candidate for candidate in codes if code.startswith(candidate) and candidate != code)
        parent = max(parents, key=len, default=None)
        account_type = "parent" if any(other.startswith(code) for other in codes if other != code) else "account"
        if parent is None:
            parent = code[0]
        hierarchy_level = HIERARCHY_LEVELS[len(code)]
        records.append((
            code,
            account["label_fr"],
            parent,
            account_type,
            hierarchy_level,
            "pcge_pdf",
        ))
    return records


def seed_database(database_path: str | Path, accounts: list[dict[str, Any]]) -> dict[str, int]:
    """Completely replace the PCGE catalog and its stale auxiliary-account rows."""
    codes = [str(account.get("account_code", "")) for account in accounts]
    if any(
        not code.isdigit()
        or len(code) not in HIERARCHY_LEVELS
        or code[0] not in "12345678"
        or int(account.get("class", -1)) != int(code[0])
        for account, code in zip(accounts, codes)
    ):
        raise ValueError("PCGE seed records must use official 2- to 5-digit account codes")
    if len(codes) != len(set(codes)):
        raise ValueError("PCGE seed records contain duplicate account codes")
    path = Path(database_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        db.execute(PCM_TABLE_DDL)
        columns = {row["name"] for row in db.execute("PRAGMA table_info(pcm_accounts)")}
        if "catalog_source" not in columns:
            db.execute("ALTER TABLE pcm_accounts ADD COLUMN catalog_source TEXT NOT NULL DEFAULT 'existing'")
        if "hierarchy_level" not in columns:
            db.execute("ALTER TABLE pcm_accounts ADD COLUMN hierarchy_level TEXT NOT NULL DEFAULT 'account'")

        db.execute(
            "CREATE TEMP TABLE pcge_seed (code TEXT PRIMARY KEY, label TEXT NOT NULL, parent TEXT, "
            "account_type TEXT NOT NULL, hierarchy_level TEXT NOT NULL, catalog_source TEXT NOT NULL)"
        )
        records = _database_records(accounts)
        db.executemany("INSERT INTO pcge_seed VALUES (?, ?, ?, ?, ?, ?)", records)
        tables = {row["name"] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

        db.execute("BEGIN IMMEDIATE")
        before_count = db.execute("SELECT COUNT(*) FROM pcm_accounts").fetchone()[0]
        auxiliary_count = (
            db.execute("SELECT COUNT(*) FROM auxiliary_accounts").fetchone()[0]
            if "auxiliary_accounts" in tables else 0
        )
        if "auxiliary_accounts" in tables:
            db.execute("DELETE FROM auxiliary_accounts")
        db.execute("DELETE FROM pcm_accounts")
        db.execute(
            """INSERT INTO pcm_accounts(code, label, parent, account_type, hierarchy_level, catalog_source, updated_at)
               SELECT code, label, parent, account_type, hierarchy_level, catalog_source, CURRENT_TIMESTAMP
               FROM pcge_seed WHERE 1
               ON CONFLICT(code) DO UPDATE SET label=excluded.label, parent=excluded.parent,
                 account_type=excluded.account_type, hierarchy_level=excluded.hierarchy_level,
                 catalog_source=excluded.catalog_source,
                 updated_at=excluded.updated_at"""
        )
        violations = db.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError(f"PCGE reseed would violate database foreign keys: {violations!r}")
        final_count = db.execute("SELECT COUNT(*) FROM pcm_accounts").fetchone()[0]
        db.commit()
        return {
            "seeded": final_count,
            "removed": before_count,
            "added": final_count,
            "removed_auxiliary": auxiliary_count,
        }
    except Exception:
        if db.in_transaction:
            db.rollback()
        raise
    finally:
        db.close()


def write_dataset(path: str | Path, accounts: list[dict[str, Any]]) -> None:
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(accounts, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, help="Path to the official PCGE PDF")
    parser.add_argument(
        "--database",
        default=str(PROJECT_ROOT / "kompta.sqlite3"),
        help="SQLite database to seed (default: project database)",
    )
    args = parser.parse_args()

    accounts = extract_pcge_accounts(args.pdf)
    write_dataset(DATASET_PATH, accounts)
    report = seed_database(args.database, accounts)
    print(
        f"PCGE seeded: {report['seeded']} hierarchy rows "
        f"({len(accounts)} accounts and 8 classes); "
        f"{report['removed']} old accounts and {report['removed_auxiliary']} old auxiliaries purged."
    )


if __name__ == "__main__":
    main()
