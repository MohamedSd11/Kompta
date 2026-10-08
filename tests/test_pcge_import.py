from __future__ import annotations

from core import journal_service
from core.journal_service import JournalRepository
from core.pcge_import import parse_pcge_text, preview_import


def test_parser_keeps_general_business_classes_and_excludes_special_classes():
    text = """Classe 1
11
CAPITAUX PROPRES
1111
Capital social
Classe 9
90
Analytique
Classe 0
01
Bilan d'ouverture
"""

    accounts = parse_pcge_text(text)

    assert [item["code"] for item in accounts] == ["11", "1111"]
    assert accounts[1]["label"] == "Capital social"


def test_preview_reports_missing_present_and_review_without_relabeling_existing():
    source = [
        {"code": "1111", "label": "Capital social", "class": 1, "source": "pcge_general"},
        {"code": "1112", "label": "Fonds de dotation", "class": 1, "source": "pcge_general"},
        {"code": "1117", "label": "Capital personnel", "class": 1, "source": "pcge_general", "needs_review": True, "review_reason": "source_text_encoding"},
    ]

    # Exercise the pure comparison contract without reading or modifying a database.
    import core.pcge_import as pcge_import
    original = pcge_import.extract_pcge_general_accounts
    pcge_import.extract_pcge_general_accounts = lambda _path=None: source
    try:
        report = preview_import([{"code": "1111", "label": "Custom label"}])
    finally:
        pcge_import.extract_pcge_general_accounts = original

    assert [item["code"] for item in report["added"]] == ["1112"]
    assert report["alreadyPresent"][0]["currentLabel"] == "Custom label"
    assert [item["code"] for item in report["needsReview"]] == ["1117"]


def test_import_is_idempotent_and_preserves_existing_catalog_and_entries(tmp_path, monkeypatch):
    source = [
        {"code": "1111", "label": "Capital social", "class": 1, "source": "pcge_general"},
        {"code": "1112", "label": "Fonds de dotation", "class": 1, "source": "pcge_general"},
    ]
    monkeypatch.setattr(journal_service, "extract_pcge_general_accounts", lambda _path=None: source)
    import core.pcge_import as pcge_import
    monkeypatch.setattr(pcge_import, "extract_pcge_general_accounts", lambda _path=None: source)
    monkeypatch.setattr(journal_service, "preview_import", preview_import)

    repository = JournalRepository(tmp_path / "pcge.sqlite3")
    with repository._connect() as db:
        db.execute("INSERT INTO pcm_accounts(code, label, account_type, updated_at) VALUES ('1111', 'Custom label', 'parent', 'now')")
        db.execute("INSERT INTO journal_entries(client_id, year, entry_number, piece_number, journal, entry_date, user_id, posted_at) VALUES ('C001', 2026, 1, 'OD-000001', 'OD', '2026-01-01', 'user', 'now')")

    first = repository.import_pcge_general()
    second = repository.import_pcge_general()

    assert [item["code"] for item in first["imported"]] == ["1112"]
    assert second["imported"] == []
    with repository._connect() as db:
        assert db.execute("SELECT label FROM pcm_accounts WHERE code='1111'").fetchone()[0] == "Custom label"
        assert db.execute("SELECT COUNT(*) FROM pcm_accounts WHERE code='1112'").fetchone()[0] == 1
        assert db.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0] == 1
