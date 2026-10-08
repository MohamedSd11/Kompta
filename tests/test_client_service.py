import sqlite3

import pytest
from pydantic import ValidationError

from core.client_service import ClientRepository, ClientUpsert, FiscalYearUpsert


def client_request(name="SARL Réelle"):
    return ClientUpsert(
        name=name,
        ice="123456789012345",
        legalForm="SARL",
        tvaRegime="Débit",
        tvaPeriodicite="Mensuelle",
    )


def test_real_client_and_fiscal_year_round_trip(tmp_path):
    repository = ClientRepository(tmp_path / "kompta.sqlite3")

    created = repository.create_client(client_request())
    assert created["isDemo"] is False
    assert created["years"] == []

    saved_year = repository.save_fiscal_year(created["id"], FiscalYearUpsert(year=2026, status="open"))
    assert saved_year == {"clientId": created["id"], "year": 2026, "status": "open", "isDemo": False}

    updated = repository.update_client(created["id"], client_request("SARL Modifiée"))
    assert updated["name"] == "SARL Modifiée"
    assert updated["years"] == [{"year": 2026, "status": "open", "isDemo": False}]

    assert repository.list_clients(include_demo=False) == [updated]

    restarted_repository = ClientRepository(tmp_path / "kompta.sqlite3")
    assert restarted_repository.list_clients(include_demo=False) == [updated]


def test_fiscal_year_save_is_upsert(tmp_path):
    repository = ClientRepository(tmp_path / "kompta.sqlite3")
    created = repository.create_client(client_request())

    repository.save_fiscal_year(created["id"], FiscalYearUpsert(year=2026, status="open"))
    repository.save_fiscal_year(created["id"], FiscalYearUpsert(year=2026, status="closed"))

    assert repository.get_client(created["id"])["years"] == [
        {"year": 2026, "status": "closed", "isDemo": False}
    ]


def test_demo_records_are_excluded_from_real_client_listing(tmp_path):
    repository = ClientRepository(tmp_path / "kompta.sqlite3")
    real = repository.create_client(client_request())
    now = repository._now()
    with repository._connect() as db:
        db.execute(
            """INSERT INTO clients(id, name, ice, legal_form, tva_regime, tva_periodicite, is_demo, created_at, updated_at)
               VALUES ('D001', 'Client Démo', '999999999999999', 'SARL', 'Débit', 'Mensuelle', 1, ?, ?)""",
            (now, now),
        )
        db.execute(
            """INSERT INTO fiscal_years(client_id, year, status, is_demo, created_at, updated_at)
               VALUES ('D001', 2026, 'open', 1, ?, ?)""",
            (now, now),
        )

    assert [client["id"] for client in repository.list_clients(include_demo=False)] == [real["id"]]
    assert {client["id"] for client in repository.list_clients(include_demo=True)} == {real["id"], "D001"}


def test_duplicate_real_ice_is_rejected_without_overwriting_existing_client(tmp_path):
    repository = ClientRepository(tmp_path / "kompta.sqlite3")
    first = repository.create_client(client_request("Premier client"))

    with pytest.raises(sqlite3.IntegrityError):
        repository.create_client(client_request("Deuxième client"))

    assert repository.get_client(first["id"])["name"] == "Premier client"
    assert len(repository.list_clients(include_demo=False)) == 1


def test_invalid_client_and_fiscal_year_data_is_rejected(tmp_path):
    with pytest.raises(ValidationError):
        ClientUpsert(name="", legalForm="SARL")
    with pytest.raises(ValidationError):
        ClientUpsert(name="Client", ice="123", legalForm="SARL")
    with pytest.raises(ValidationError):
        FiscalYearUpsert(year=1999)
    with pytest.raises(ValidationError):
        FiscalYearUpsert(year=2026, status="invalid")
