from __future__ import annotations

import sqlite3

from core.journal_service import JournalRepository
from tools.seed_pcge import parse_pcge_page, seed_database


def test_parse_pcge_page_keeps_account_labels_and_removes_list_bullets():
    accounts = parse_pcge_page(
        "CLASSE 5 : TRÉSORERIE\n"
        "5141 Banques (soldes débiteurs)\n"
        "51611 - Caisse centrale\n"
        "N° Compte Intitulé du Compte\n"
        "Page 15 sur 29\n",
        15,
    )

    assert [(row["account_code"], row["label_fr"], row["class"], row["page_pdf"]) for row in accounts] == [
        ("5141", "Banques (soldes débiteurs)", 5, 15),
        ("51611", "Caisse centrale", 5, 15),
    ]


def test_seed_purges_old_accounts_and_auxiliaries_and_builds_hierarchy(tmp_path):
    database = tmp_path / "kompta.sqlite3"
    with sqlite3.connect(database) as db:
        db.execute(
            """CREATE TABLE pcm_accounts (
                code TEXT PRIMARY KEY, label TEXT NOT NULL, parent TEXT,
                account_type TEXT NOT NULL DEFAULT 'parent',
                catalog_source TEXT NOT NULL DEFAULT 'existing', updated_at TEXT NOT NULL
            )"""
        )
        db.execute(
            """CREATE TABLE auxiliary_accounts (
                code TEXT NOT NULL, label TEXT NOT NULL, root_code TEXT NOT NULL,
                client_id TEXT NOT NULL, ice TEXT, tax_id TEXT, account_type TEXT NOT NULL,
                updated_at TEXT NOT NULL, FOREIGN KEY(root_code) REFERENCES pcm_accounts(code)
            )"""
        )
        db.execute("CREATE TABLE journal_entries (id INTEGER PRIMARY KEY, label TEXT NOT NULL)")
        db.executemany(
            "INSERT INTO pcm_accounts(code, label, updated_at) VALUES (?, ?, 'old')",
            [("9999", "Orange Maroc",), ("1111", "Ancien libellé"), ("4411", "Fournisseurs")],
        )
        db.execute(
            "INSERT INTO auxiliary_accounts(code, label, root_code, client_id, account_type, updated_at) "
            "VALUES ('44110001', 'Fournisseur A', '4411', 'C001', 'Fournisseur', 'old')"
        )
        db.execute("INSERT INTO journal_entries(label) VALUES ('Écriture conservée')")

    accounts = [
        {"account_code": "1111", "label_fr": "Capital social", "class": 1},
        {"account_code": "4411", "label_fr": "Fournisseurs", "class": 4},
        {"account_code": "5141", "label_fr": "Banques (soldes débiteurs)", "class": 5},
    ]
    report = seed_database(database, accounts)

    repository = JournalRepository(database)
    assert next(
        account["label"] for account in repository.list_pcge_accounts() if account["code"] == "5141"
    ) == "Banques (soldes débiteurs)"
    chart = {account["code"]: account for account in repository.list_pcge_accounts()}
    assert chart["1"] == {
        "code": "1",
        "label": "FINANCEMENT PERMANENT",
        "class": 1,
        "classLabel": "FINANCEMENT PERMANENT",
        "parent": None,
        "level": "class",
        "status": "standard",
        "source": "pcge_pdf",
        "type": "parent",
    }
    assert (chart["1111"]["parent"], chart["1111"]["level"]) == ("1", "principal")
    assert (chart["4411"]["parent"], chart["4411"]["level"]) == ("4", "principal")
    assert repository.search_pcge_accounts("5141") == [
        {"code": "5141", "label": "Banques (soldes débiteurs)", "class": 5}
    ]
    db = repository._connect()
    with db:
        repository._sync_catalog(db, [
            {"code": "44110001", "label": "Orange Maroc", "type": "divisionnaire"},
            {"code": "5141", "label": "Faux libellé", "type": "parent"},
        ])
    db.close()
    with sqlite3.connect(database) as db:
        assert {row[0] for row in db.execute("SELECT code FROM pcm_accounts")} == {
            "1", "2", "3", "4", "5", "6", "7", "8", "1111", "4411", "5141"
        }
        assert db.execute("SELECT COUNT(*) FROM pcm_accounts WHERE length(code) > 5").fetchone()[0] == 0
        assert db.execute("SELECT label FROM pcm_accounts WHERE code='1111'").fetchone()[0] == "Capital social"
        assert db.execute("SELECT label FROM pcm_accounts WHERE code='5141'").fetchone()[0] == "Banques (soldes débiteurs)"
        assert db.execute("SELECT COUNT(*) FROM auxiliary_accounts").fetchone()[0] == 0
        assert db.execute("SELECT label FROM journal_entries").fetchone()[0] == "Écriture conservée"
    assert report == {"seeded": 11, "removed": 3, "added": 11, "removed_auxiliary": 1}


def test_seed_rejects_local_divisionary_codes(tmp_path):
    database = tmp_path / "kompta.sqlite3"
    try:
        seed_database(database, [
            {"account_code": "44110001", "label_fr": "Orange Maroc", "class": 4},
        ])
    except ValueError as error:
        assert "official 2- to 5-digit" in str(error)
    else:
        raise AssertionError("A local auxiliary code must not enter the official PCGE catalog")
