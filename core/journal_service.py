"""Append-only journal posting service for Kompta.

The browser may prepare a draft, but only this module can allocate numbers and
persist a posted entry. SQLite transactions are serialized with BEGIN IMMEDIATE;
triggers make posted journal data and audit records immutable.
"""
from __future__ import annotations

import json
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .storage import connect_database, resolve_database_path, utc_now_iso
from .pcge_import import preview_import, extract_pcge_general_accounts
from .cgnc import (
    TIER_ROOT_TYPES,
    TIER_ROOTS,
    is_listed_cgnc_account,
    official_label,
)


JOURNAL_PIECE_PREFIXES = {"ACHATS": "JA", "VENTES": "JV", "BANQUE": "JB", "CAISSE": "JC"}
AUXILIARY_ACCOUNTS_DDL = """
    CREATE TABLE IF NOT EXISTS auxiliary_accounts (
        code TEXT NOT NULL,
        label TEXT NOT NULL,
        root_code TEXT NOT NULL,
        client_id TEXT NOT NULL,
        ice TEXT,
        tax_id TEXT,
        account_type TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY(client_id, code),
        FOREIGN KEY(root_code) REFERENCES pcm_accounts(code)
    );
"""


class JournalLine(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    account: str = Field(..., min_length=1, alias="compte")
    auxiliary: str | None = Field(None, alias="auxiliaire")
    label: str = Field("", alias="libelle")
    debit: float = Field(0, ge=0)
    credit: float = Field(0, ge=0)
    invoice: str = Field("", alias="facture")
    vat_rate: float = Field(0, ge=0, alias="tva")

    @model_validator(mode="after")
    def one_side_only(self) -> "JournalLine":
        if self.debit and self.credit:
            raise ValueError("A journal line cannot contain both debit and credit")
        if not self.debit and not self.credit:
            raise ValueError("A journal line must contain a debit or a credit")
        return self


class JournalEntryPost(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: str = Field("local-owner", min_length=1, alias="userId")
    client_id: str = Field(..., min_length=1, alias="clientId")
    year: int = Field(..., ge=2000, le=2100)
    journal: str = Field(..., min_length=1)
    entry_date: str = Field(..., min_length=8, alias="date")
    piece_number_hint: str = Field("", alias="pieceNumber")
    reference: str = Field("", alias="reference")
    label: str = Field("", alias="libelle")
    lines: list[JournalLine] = Field(..., min_length=2)
    account_catalog: list[dict[str, Any]] = Field(default_factory=list, alias="accountCatalog")
    auxiliary_catalog: list[dict[str, Any]] = Field(default_factory=list, alias="auxiliaryCatalog")
    cash_opening_balance: float = Field(0, ge=0, alias="cashOpeningBalance")
    draft_id: str | None = Field(None, alias="draftId")

    @field_validator("journal")
    @classmethod
    def normalize_journal(cls, value: str) -> str:
        normalized = value.strip().upper()
        aliases = {"VT": "VENTES", "AC": "ACHATS", "BQ": "BANQUE", "CA": "CAISSE"}
        normalized = aliases.get(normalized, normalized)
        if not normalized:
            raise ValueError("Journal auxiliaire inconnu")
        return normalized

    @field_validator("entry_date")
    @classmethod
    def validate_entry_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError("Date d’écriture invalide; format attendu AAAA-MM-JJ") from error
        return value


class JournalDraftSave(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    draft_id: str | None = Field(None, alias="draftId")
    user_id: str = Field("local-owner", min_length=1, alias="userId")
    client_id: str = Field(..., min_length=1, alias="clientId")
    year: int = Field(..., ge=2000, le=2100)
    journal: str = Field(..., min_length=1)
    entry_date: str = Field(..., min_length=8, alias="date")
    reference: str = Field("", alias="reference")
    label: str = Field("", alias="libelle")
    operation: str = Field("", alias="operation")
    lines: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("journal")
    @classmethod
    def normalize_journal(cls, value: str) -> str:
        normalized = value.strip().upper()
        aliases = {"VT": "VENTES", "AC": "ACHATS", "BQ": "BANQUE", "CA": "CAISSE"}
        return aliases.get(normalized, normalized)


class JournalEntryPosted(BaseModel):
    entry_id: int = Field(alias="entryId")
    entry_number: int = Field(alias="entryNumber")
    piece_number: str = Field(alias="pieceNumber")
    client_id: str = Field(alias="clientId")
    year: int
    model_config = ConfigDict(populate_by_name=True)


class JournalRepository:
    def __init__(self, database: str | Path | None = None) -> None:
        self.database = str(resolve_database_path(database))
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return connect_database(self.database, autocommit=True)

    def _initialize(self) -> None:
        with closing(self._connect()) as db, db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS pcm_accounts (
                    code TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    parent TEXT,
                    account_type TEXT NOT NULL DEFAULT 'parent',
                    hierarchy_level TEXT NOT NULL DEFAULT 'account',
                    catalog_source TEXT NOT NULL DEFAULT 'existing',
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    entry_number INTEGER NOT NULL,
                    piece_number TEXT NOT NULL,
                    journal TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    reference TEXT NOT NULL DEFAULT '',
                    label TEXT NOT NULL DEFAULT '',
                    user_id TEXT NOT NULL,
                    posted_at TEXT NOT NULL,
                    UNIQUE(client_id, year, entry_number),
                    UNIQUE(client_id, year, piece_number)
                );
                CREATE TABLE IF NOT EXISTS journal_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id INTEGER NOT NULL REFERENCES journal_entries(id),
                    line_number INTEGER NOT NULL,
                    account_code TEXT NOT NULL,
                    auxiliary_code TEXT,
                    label TEXT NOT NULL DEFAULT '',
                    debit NUMERIC NOT NULL DEFAULT 0,
                    credit NUMERIC NOT NULL DEFAULT 0,
                    invoice TEXT NOT NULL DEFAULT '',
                    vat_rate NUMERIC NOT NULL DEFAULT 0,
                    UNIQUE(entry_id, line_number)
                );
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL CHECK(action_type IN ('CREATE','POST','REVERSAL')),
                    entry_id INTEGER NOT NULL,
                    payload_diff TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS journal_sequences (
                    client_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    next_entry_number INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY(client_id, year)
                );
                CREATE TABLE IF NOT EXISTS journal_cash_opening_balances (
                    client_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    opening_balance NUMERIC NOT NULL CHECK(opening_balance >= 0),
                    PRIMARY KEY(client_id, year)
                );
                CREATE TABLE IF NOT EXISTS journal_drafts (
                    draft_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    journal TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    reference TEXT NOT NULL DEFAULT '',
                    label TEXT NOT NULL DEFAULT '',
                    operation TEXT NOT NULL DEFAULT '',
                    lines_json TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('DRAFT', 'VALIDATED')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    posted_entry_id INTEGER REFERENCES journal_entries(id)
                );
                CREATE TRIGGER IF NOT EXISTS journal_entries_no_update
                BEFORE UPDATE ON journal_entries BEGIN SELECT RAISE(ABORT, 'posted journal entries are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS journal_entries_no_delete
                BEFORE DELETE ON journal_entries BEGIN SELECT RAISE(ABORT, 'posted journal entries are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS journal_lines_no_update
                BEFORE UPDATE ON journal_lines BEGIN SELECT RAISE(ABORT, 'posted journal lines are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS journal_lines_no_delete
                BEFORE DELETE ON journal_lines BEGIN SELECT RAISE(ABORT, 'posted journal lines are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS audit_logs_no_update
                BEFORE UPDATE ON audit_logs BEGIN SELECT RAISE(ABORT, 'audit logs are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS audit_logs_no_delete
                BEFORE DELETE ON audit_logs BEGIN SELECT RAISE(ABORT, 'audit logs are immutable'); END;
                """
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(pcm_accounts)").fetchall()}
            if "catalog_source" not in columns:
                db.execute("ALTER TABLE pcm_accounts ADD COLUMN catalog_source TEXT NOT NULL DEFAULT 'existing'")
            if "hierarchy_level" not in columns:
                db.execute("ALTER TABLE pcm_accounts ADD COLUMN hierarchy_level TEXT NOT NULL DEFAULT 'account'")
            self._ensure_auxiliary_accounts_table(db)
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS journal_account_migrations (
                    migration_key TEXT PRIMARY KEY,
                    migrated_at TEXT NOT NULL,
                    migrated_lines_json TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS journal_account_migrations_no_update
                BEFORE UPDATE ON journal_account_migrations BEGIN SELECT RAISE(ABORT, 'journal migrations are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS journal_account_migrations_no_delete
                BEFORE DELETE ON journal_account_migrations BEGIN SELECT RAISE(ABORT, 'journal migrations are immutable'); END;
                """
            )
            self._migrate_legacy_tier_accounts(db)

    @staticmethod
    def _ensure_auxiliary_accounts_table(db: sqlite3.Connection) -> None:
        info = db.execute("PRAGMA table_info(auxiliary_accounts)").fetchall()
        if not info:
            db.executescript(AUXILIARY_ACCOUNTS_DDL)
            return
        primary_key = [row[1] for row in sorted(info, key=lambda row: row[5]) if row[5]]
        if primary_key == ["client_id", "code"]:
            return
        # Legacy schema keyed on code alone; shared supplier/client codes need per-dossier rows.
        db.executescript(
            "BEGIN IMMEDIATE;"
            "ALTER TABLE auxiliary_accounts RENAME TO auxiliary_accounts_legacy;"
            + AUXILIARY_ACCOUNTS_DDL
            + "INSERT INTO auxiliary_accounts(code, label, root_code, client_id, ice, tax_id, account_type, updated_at)"
            " SELECT code, label, root_code, client_id, ice, tax_id, account_type, updated_at FROM auxiliary_accounts_legacy;"
            "DROP TABLE auxiliary_accounts_legacy;"
            "COMMIT;"
        )

    @staticmethod
    def _now() -> str:
        return utc_now_iso()

    def _migrate_legacy_tier_accounts(self, db: sqlite3.Connection) -> None:
        migration_key = "tier_account_codes_to_auxiliary_v1"
        entry_columns = {row["name"] for row in db.execute("PRAGMA table_info(journal_entries)")}
        line_columns = {row["name"] for row in db.execute("PRAGMA table_info(journal_lines)")}
        if not {"id", "client_id"}.issubset(entry_columns) or not {
            "id", "entry_id", "account_code", "auxiliary_code", "label"
        }.issubset(line_columns):
            return
        if db.execute(
            "SELECT 1 FROM journal_account_migrations WHERE migration_key=?",
            (migration_key,),
        ).fetchone():
            return

        db.execute("BEGIN IMMEDIATE")
        migrated = []
        try:
            rows = db.execute(
                """SELECT l.id, l.entry_id, l.account_code, l.auxiliary_code, l.label,
                          e.client_id
                   FROM journal_lines l
                   JOIN journal_entries e ON e.id=l.entry_id
                   WHERE (l.account_code LIKE '3421%' OR l.account_code LIKE '4411%')
                     AND length(l.account_code)=8"""
            ).fetchall()
            db.execute("DROP TRIGGER IF EXISTS journal_lines_no_update")
            for row in rows:
                legacy_code = row["account_code"]
                if is_listed_cgnc_account(legacy_code):
                    continue
                root_code = legacy_code[:4]
                auxiliary_code = row["auxiliary_code"] or legacy_code
                chart_label = db.execute(
                    "SELECT label FROM pcm_accounts WHERE code=?", (legacy_code,)
                ).fetchone()
                auxiliary_label = (
                    chart_label["label"] if chart_label else row["label"] or f"Tiers {legacy_code}"
                )
                db.execute(
                    """INSERT OR IGNORE INTO pcm_accounts(
                           code, label, parent, account_type, hierarchy_level, catalog_source, updated_at
                       ) VALUES (?, ?, ?, 'parent', 'principal', 'cgnc_standard', ?)""",
                    (root_code, official_label(root_code) or root_code, root_code[0], self._now()),
                )
                db.execute(
                    """INSERT OR IGNORE INTO auxiliary_accounts(
                           code, label, root_code, client_id, account_type, updated_at
                       ) VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        auxiliary_code, auxiliary_label, root_code, row["client_id"],
                        TIER_ROOT_TYPES[root_code], self._now(),
                    ),
                )
                db.execute(
                    """UPDATE journal_lines
                       SET account_code=?, auxiliary_code=COALESCE(NULLIF(auxiliary_code, ''), ?)
                       WHERE id=?""",
                    (root_code, auxiliary_code, row["id"]),
                )
                migrated.append({
                    "lineId": row["id"],
                    "entryId": row["entry_id"],
                    "oldAccount": legacy_code,
                    "account": root_code,
                    "auxiliary": auxiliary_code,
                })
            legacy_codes = {
                row["account_code"] for row in rows
                if not is_listed_cgnc_account(row["account_code"])
            }
            legacy_codes.update(
                row["code"] for row in db.execute(
                    """SELECT code FROM pcm_accounts
                       WHERE length(code)=8 AND (code LIKE '3421%' OR code LIKE '4411%')"""
                )
                if not is_listed_cgnc_account(row["code"])
            )
            db.executemany(
                """DELETE FROM pcm_accounts
                   WHERE code=? AND length(code)=8
                     AND (code LIKE '3421%' OR code LIKE '4411%')""",
                [(code,) for code in legacy_codes],
            )
            db.execute(
                """CREATE TRIGGER journal_lines_no_update
                   BEFORE UPDATE ON journal_lines
                   BEGIN SELECT RAISE(ABORT, 'posted journal lines are immutable'); END"""
            )
            db.execute(
                """INSERT INTO journal_account_migrations(migration_key, migrated_at, migrated_lines_json)
                   VALUES (?, ?, ?)""",
                (migration_key, self._now(), json.dumps(migrated, sort_keys=True)),
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

    def _sync_catalog(self, db: sqlite3.Connection, catalog: list[dict[str, Any]]) -> None:
        """Mirror exact official PCGE codes, never local extensions, into the PCGE table."""
        now = self._now()
        for account in catalog:
            code = str(account.get("code", "")).strip()
            label = official_label(code)
            if not label or not is_listed_cgnc_account(code):
                continue
            db.execute(
                """INSERT OR IGNORE INTO pcm_accounts(code, label, parent, account_type, hierarchy_level, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """,
                (
                    code,
                    label,
                    account.get("parent"),
                    account.get("type", "parent"),
                    account.get("hierarchy_level", account.get("hierarchyLevel", "account")),
                    now,
                ),
            )

    def list_pcge_accounts(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as db, db:
            rows = db.execute(
                """SELECT code, label, parent, account_type, hierarchy_level, catalog_source
                   FROM pcm_accounts ORDER BY code"""
            ).fetchall()
        if not rows:
            raise RuntimeError("PCGE database is empty; run tools/seed_pcge.py with the official PDF.")
        return [
            {
                "code": row["code"],
                "label": row["label"],
                "class": int(row["code"][0]),
                "classLabel": row["label"] if row["hierarchy_level"] == "class" else None,
                "parent": row["parent"],
                "level": row["hierarchy_level"],
                "status": "standard",
                "source": row["catalog_source"],
                "type": row["account_type"],
            }
            for row in rows
            if is_listed_cgnc_account(row["code"])
            or (row["hierarchy_level"] == "class" and row["code"] in "12345678")
        ]

    def search_pcge_accounts(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        term = query.strip()
        if not term:
            raise ValueError("PCGE account search query cannot be empty")
        escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        with closing(self._connect()) as db, db:
            rows = db.execute(
                """SELECT code, label FROM pcm_accounts
                   WHERE hierarchy_level != 'class'
                     AND length(code) BETWEEN 4 AND 5
                     AND (code LIKE ? ESCAPE '\\' OR lower(label) LIKE ? ESCAPE '\\')
                   ORDER BY CASE WHEN code = ? THEN 0 WHEN code LIKE ? ESCAPE '\\' THEN 1 ELSE 2 END, code
                   LIMIT ?""",
                (escaped + "%", "%" + escaped.lower() + "%", term, escaped + "%", limit),
            ).fetchall()
            seeded = db.execute("SELECT EXISTS(SELECT 1 FROM pcm_accounts)").fetchone()[0]
        if not seeded:
            raise RuntimeError("PCGE database is empty; run tools/seed_pcge.py with the official PDF.")
        return [
            {"code": row["code"], "label": row["label"], "class": int(row["code"][0])}
            for row in rows
            if is_listed_cgnc_account(row["code"])
        ][:limit]

    def _sync_auxiliary_accounts(self, db: sqlite3.Connection, client_id: str, catalog: list[dict[str, Any]]) -> None:
        """Register third-party contacts independently from general ledger accounts."""
        now = self._now()
        for account in catalog:
            code = str(account.get("compte_auxiliaire", account.get("code", ""))).strip()
            root = str(account.get("compte_racine", account.get("parent", ""))).strip()
            if root not in TIER_ROOT_TYPES or not code.startswith(root) or len(code) <= 4 or not code.isdigit():
                continue
            label = str(account.get("libelle", account.get("label", ""))).strip()
            if not label:
                continue
            db.execute(
                """INSERT OR IGNORE INTO pcm_accounts(code, label, account_type, catalog_source, updated_at)
                   VALUES (?, ?, 'parent', 'cgnc_standard', ?)""",
                (root, official_label(root) or root, now),
            )
            db.execute(
                """INSERT INTO auxiliary_accounts(code, label, root_code, client_id, ice, tax_id, account_type, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(client_id, code) DO UPDATE SET label=excluded.label, ice=excluded.ice,
                     tax_id=excluded.tax_id, account_type=excluded.account_type, updated_at=excluded.updated_at""",
                (
                    code, label, root, client_id,
                    str(account.get("ice") or "").strip() or None,
                    str(account.get("identifiant_fiscal") or account.get("identifiantFiscal") or "").strip() or None,
                    str(account.get("type_tiers") or account.get("type") or TIER_ROOT_TYPES[root]),
                    now,
                ),
            )

    def preview_pcge_general(self, source_path: str | Path | None = None, existing: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        with closing(self._connect()) as db, db:
            catalog = existing
            if catalog is None:
                catalog = [dict(row) for row in db.execute("SELECT code, label, parent, account_type AS type FROM pcm_accounts").fetchall()]
        return preview_import(catalog, source_path)

    def import_pcge_general(self, source_path: str | Path | None = None, existing: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        report = self.preview_pcge_general(source_path, existing)
        now = self._now()
        imported = []
        codes = {item["code"] for item in extract_pcge_general_accounts(source_path)}
        with closing(self._connect()) as db, db:
            for account in report["added"]:
                cursor = db.execute(
                    """INSERT OR IGNORE INTO pcm_accounts(code, label, parent, account_type, catalog_source, updated_at)
                       VALUES (?, ?, ?, ?, 'cgnc_standard', ?)""",
                    (account["code"], account["label"], account.get("parent"), "parent" if any(code.startswith(account["code"]) and code != account["code"] for code in codes) else "account", now),
                )
                if cursor.rowcount:
                    imported.append(account)
        report["imported"] = imported
        report["importedCount"] = len(imported)
        return report

    def _validate_lines(
        self, db: sqlite3.Connection, request: JournalEntryPost, *, reversal: bool = False
    ) -> None:
        debit = sum(line.debit for line in request.lines)
        credit = sum(line.credit for line in request.lines)
        if round(debit - credit, 2) != 0 or debit <= 0:
            raise ValueError("Journal entry must be balanced and have a positive total")
        if request.journal == "AUDIT":
            raise ValueError("Le journal Audit est en lecture seule")
        if not reversal and request.journal in {"VENTES", "ACHATS"} and not request.reference.strip():
            required = "N° facture client" if request.journal == "VENTES" else "N° Facture Fournisseur"
            raise ValueError(f"{required} obligatoire")
        for line in request.lines:
            if not reversal and (
                len(line.account) not in {4, 5}
                or not line.account.isdigit()
                or not is_listed_cgnc_account(line.account)
            ):
                raise ValueError(f"Compte général absent du référentiel CGNC: {line.account}")
            if line.account in TIER_ROOTS:
                if not line.auxiliary:
                    raise ValueError(f"Auxiliary account is required for tier account {line.account}")
                auxiliary = db.execute(
                    "SELECT root_code FROM auxiliary_accounts WHERE code = ? AND client_id = ?",
                    (line.auxiliary.strip(), request.client_id),
                ).fetchone()
                if auxiliary is None or not line.auxiliary.startswith(line.account[:4]):
                    raise ValueError(f"Invalid auxiliary account for tier account {line.account}")

        fixed_account = {"BANQUE": "5141", "CAISSE": "5161"}.get(request.journal)
        if fixed_account:
            fixed_lines = [line for line in request.lines if line.account == fixed_account]
            if len(fixed_lines) != 1:
                raise ValueError(f"Le compte {fixed_account} doit apparaître exactement une fois")
            fixed_line = fixed_lines[0]
            if not reversal:
                expected_root = "3421" if fixed_line.debit else "4411"
                if not any(
                    line is not fixed_line and line.account.startswith(expected_root)
                    and (line.credit if fixed_line.debit else line.debit) > 0
                    for line in request.lines
                ):
                    raise ValueError(
                        "Un encaissement doit être équilibré par un client 3421; "
                        "un décaissement par un fournisseur 4411"
                    )
            if not reversal and request.journal == "BANQUE" and not request.reference.strip():
                raise ValueError("Référence / Mode de règlement obligatoire")

        if not reversal and request.journal == "VENTES":
            if not any(line.account == "3421" and line.debit > 0 for line in request.lines):
                raise ValueError("Le journal des ventes doit débiter un compte client 3421")
            if not any(line.account.startswith("7") and line.credit > 0 for line in request.lines):
                raise ValueError("Le journal des ventes doit créditer un compte de produits de classe 7")
            if not any(line.account == "4455" and line.credit > 0 for line in request.lines):
                raise ValueError("Le journal des ventes doit créditer la TVA facturée 4455")
        if not reversal and request.journal == "ACHATS":
            if not any(line.account.startswith("6") and line.debit > 0 for line in request.lines):
                raise ValueError("Le journal des achats doit débiter un compte de charges de classe 6")
            if not any(line.account in {"3455", "34552"} and line.debit > 0 for line in request.lines):
                raise ValueError("Le journal des achats doit débiter la TVA récupérable 3455")
            if not any(line.account == "4411" and line.credit > 0 for line in request.lines):
                raise ValueError("Le journal des achats doit créditer un compte fournisseur 4411")

        if request.journal == "CAISSE":
            db.execute(
                """INSERT OR IGNORE INTO journal_cash_opening_balances(client_id, year, opening_balance)
                   VALUES (?, ?, ?)""",
                (request.client_id, request.year, request.cash_opening_balance),
            )
            opening = db.execute(
                "SELECT opening_balance FROM journal_cash_opening_balances WHERE client_id=? AND year=?",
                (request.client_id, request.year),
            ).fetchone()[0]
            if abs(float(opening) - request.cash_opening_balance) >= 0.005:
                raise ValueError("Le solde d’ouverture de caisse ne correspond pas aux à-nouveaux enregistrés")
            previous = db.execute(
                """SELECT COALESCE(SUM(l.debit - l.credit), 0)
                   FROM journal_lines l JOIN journal_entries e ON e.id=l.entry_id
                   WHERE e.client_id=? AND e.year=? AND l.account_code='5161'""",
                (request.client_id, request.year),
            ).fetchone()[0]
            proposed = sum(line.debit - line.credit for line in request.lines if line.account == "5161")
            if round(float(opening) + float(previous) + proposed, 2) < 0:
                raise ValueError("Solde de caisse insuffisant")

    def post(self, request: JournalEntryPost) -> JournalEntryPosted:
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            if request.draft_id:
                draft = db.execute(
                    """SELECT status FROM journal_drafts
                       WHERE draft_id=? AND client_id=? AND year=?""",
                    (request.draft_id, request.client_id, request.year),
                ).fetchone()
                if draft is None or draft["status"] != "DRAFT":
                    raise ValueError("Brouillon introuvable ou déjà validé")
            self._sync_catalog(db, request.account_catalog)
            self._sync_auxiliary_accounts(db, request.client_id, request.auxiliary_catalog)
            result = self._post_in_transaction(db, request)
            if request.draft_id:
                db.execute(
                    """UPDATE journal_drafts SET status='VALIDATED', posted_entry_id=?, updated_at=?
                       WHERE draft_id=?""",
                    (result.entry_id, self._now(), request.draft_id),
                )
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def save_draft(self, request: JournalDraftSave) -> str:
        if request.journal == "AUDIT":
            raise ValueError("Le journal Audit est en lecture seule")
        draft_id = request.draft_id or uuid.uuid4().hex
        now = self._now()
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT client_id, year, status FROM journal_drafts WHERE draft_id=?",
                (draft_id,),
            ).fetchone()
            if existing and (
                existing["client_id"] != request.client_id
                or existing["year"] != request.year
                or existing["status"] != "DRAFT"
            ):
                raise ValueError("Brouillon introuvable ou déjà validé")
            if existing:
                db.execute(
                    """UPDATE journal_drafts
                       SET journal=?, entry_date=?, reference=?, label=?, operation=?, lines_json=?,
                           updated_at=?, user_id=?
                       WHERE draft_id=?""",
                    (
                        request.journal, request.entry_date, request.reference, request.label,
                        request.operation, json.dumps(request.lines, sort_keys=True), now,
                        request.user_id, draft_id,
                    ),
                )
            else:
                db.execute(
                    """INSERT INTO journal_drafts(
                        draft_id, client_id, year, journal, entry_date, reference, label,
                        operation, lines_json, user_id, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DRAFT', ?, ?)""",
                    (
                        draft_id, request.client_id, request.year, request.journal,
                        request.entry_date, request.reference, request.label, request.operation,
                        json.dumps(request.lines, sort_keys=True), request.user_id, now, now,
                    ),
                )
            db.commit()
            return draft_id
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def list_entries(self, client_id: str, year: int) -> list[dict[str, Any]]:
        with closing(self._connect()) as db, db:
            entries = db.execute(
                "SELECT * FROM journal_entries WHERE client_id=? AND year=? ORDER BY entry_number",
                (client_id, year),
            ).fetchall()
            lines_by_entry: dict[int, list[sqlite3.Row]] = {}
            for line in db.execute(
                """SELECT l.* FROM journal_lines l JOIN journal_entries e ON e.id = l.entry_id
                   WHERE e.client_id=? AND e.year=? ORDER BY l.entry_id, l.line_number""",
                (client_id, year),
            ):
                lines_by_entry.setdefault(line["entry_id"], []).append(line)
            reversal_rows = db.execute(
                """SELECT a.payload_diff FROM audit_logs a
                   JOIN journal_entries e ON e.id=a.entry_id
                   WHERE a.action_type='REVERSAL' AND e.client_id=? AND e.year=?""",
                (client_id, year),
            ).fetchall()
            reversed_entries = {
                details["reversedEntryId"]
                for row in reversal_rows
                for details in [json.loads(row["payload_diff"])]
                if "reversedEntryId" in details
            }
            result = []
            for entry in entries:
                lines = lines_by_entry.get(entry["id"], [])
                entry_date = entry["entry_date"]
                result.append({
                    "serverEntryId": entry["id"],
                    "piece": entry["piece_number"],
                    "journal": entry["journal"],
                    "jour": int(entry_date[8:10]),
                    "mois": int(entry_date[5:7]),
                    "year": entry["year"],
                    "libelle": entry["label"],
                    "n_facture": entry["reference"],
                    "n_mvt": entry["entry_number"],
                    "status": "REVERSED" if entry["id"] in reversed_entries else "VALIDATED",
                    "lines": [{
                        "compte": line["account_code"],
                        "auxiliaire": line["auxiliary_code"],
                        "libelle": line["label"],
                        "dbcr": "D" if line["debit"] else "C",
                        "montant": float(line["debit"] or line["credit"]),
                        "tva": float(line["vat_rate"]),
                        "facture": line["invoice"],
                        "lettre": "",
                    } for line in lines],
                })
            return result

    def list_audit_logs(self, client_id: str, year: int) -> list[dict[str, Any]]:
        """Return the immutable audit history for one dossier and fiscal year."""
        with closing(self._connect()) as db, db:
            rows = db.execute(
                """SELECT a.id, a.user_id, a.timestamp, a.action_type, a.entry_id,
                          a.payload_diff, e.piece_number, e.journal, e.entry_date, e.label
                   FROM audit_logs a
                   JOIN journal_entries e ON e.id = a.entry_id
                   WHERE e.client_id=? AND e.year=?
                   ORDER BY a.id DESC""",
                (client_id, year),
            ).fetchall()
            drafts = db.execute(
                """SELECT draft_id, user_id, updated_at, entry_date, journal, label,
                          reference, operation, lines_json
                   FROM journal_drafts
                   WHERE client_id=? AND year=? AND status='DRAFT'""",
                (client_id, year),
            ).fetchall()
        reversed_entries = {
            details.get("reversedEntryId")
            for row in rows
            if row["action_type"] == "REVERSAL"
            for details in [json.loads(row["payload_diff"])]
            if details.get("reversedEntryId") is not None
        }
        events = [
            {
                "id": row["id"],
                "userId": row["user_id"],
                "timestamp": row["timestamp"],
                "actionType": row["action_type"],
                "entryId": row["entry_id"],
                "piece": row["piece_number"],
                "journal": row["journal"],
                "entryDate": row["entry_date"],
                "label": row["label"],
                "details": json.loads(row["payload_diff"]),
                "status": "REVERSED" if row["entry_id"] in reversed_entries else "VALIDATED",
            }
            for row in rows
        ]
        events.extend(
            {
                "id": draft["draft_id"],
                "userId": draft["user_id"],
                "timestamp": draft["updated_at"],
                "actionType": "DRAFT",
                "entryId": None,
                "piece": draft["draft_id"],
                "journal": draft["journal"],
                "entryDate": draft["entry_date"],
                "label": draft["label"],
                "details": {
                    "reference": draft["reference"],
                    "operation": draft["operation"],
                    "lines": json.loads(draft["lines_json"]),
                },
                "status": "DRAFT",
            }
            for draft in drafts
        )
        return sorted(events, key=lambda event: event["timestamp"], reverse=True)

    def reverse(
        self,
        entry_id: int,
        user_id: str,
        expected_client_id: str | None = None,
        expected_year: int | None = None,
    ) -> JournalEntryPosted:
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            entry = db.execute("SELECT * FROM journal_entries WHERE id=?", (entry_id,)).fetchone()
            if entry is None:
                raise ValueError("Posted journal entry not found")
            if (
                expected_client_id is not None
                and entry["client_id"] != expected_client_id
            ) or (expected_year is not None and entry["year"] != expected_year):
                raise ValueError("Écriture introuvable dans ce dossier et cet exercice")
            reversal_rows = db.execute(
                "SELECT payload_diff FROM audit_logs WHERE action_type='REVERSAL'"
            ).fetchall()
            if any(
                json.loads(row["payload_diff"]).get("reversedEntryId") == entry_id
                for row in reversal_rows
            ):
                raise ValueError("Cette écriture a déjà été contre-passée")
            lines = db.execute("SELECT * FROM journal_lines WHERE entry_id=? ORDER BY line_number", (entry_id,)).fetchall()
            request = JournalEntryPost(
                userId=user_id, clientId=entry["client_id"], year=entry["year"], journal=entry["journal"], date=entry["entry_date"],
                reference=f"REVERSAL {entry['piece_number']}", label=f"Contre-passation de {entry['piece_number']}",
                lines=[JournalLine(compte=row["account_code"], auxiliaire=row["auxiliary_code"], libelle=f"Annulation: {row['label']}", debit=row["credit"], credit=row["debit"], facture=row["invoice"], tva=row["vat_rate"]) for row in lines],
            )
            result = self._post_in_transaction(db, request, reversal=True)
            db.execute("INSERT INTO audit_logs(user_id, timestamp, action_type, entry_id, payload_diff) VALUES (?, ?, 'REVERSAL', ?, ?)", (user_id, self._now(), result.entry_id, json.dumps({"reversedEntryId": entry_id, "sourcePiece": entry["piece_number"]})))
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _post_in_transaction(
        self, db: sqlite3.Connection, request: JournalEntryPost, *, reversal: bool = False
    ) -> JournalEntryPosted:
        self._validate_lines(db, request, reversal=reversal)
        sequence = db.execute("SELECT next_entry_number FROM journal_sequences WHERE client_id=? AND year=?", (request.client_id, request.year)).fetchone()
        number = int(sequence[0]) if sequence else 1
        if sequence:
            db.execute("UPDATE journal_sequences SET next_entry_number=? WHERE client_id=? AND year=?", (number + 1, request.client_id, request.year))
        else:
            db.execute("INSERT INTO journal_sequences VALUES (?, ?, ?)", (request.client_id, request.year, number + 1))
        prefix = JOURNAL_PIECE_PREFIXES.get(request.journal, "OD")
        existing_pieces = db.execute(
            "SELECT piece_number FROM journal_entries WHERE client_id=? AND year=? AND journal=?",
            (request.client_id, request.year, request.journal),
        ).fetchall()
        piece_number = max(
            (
                int(match.group(1))
                for row in existing_pieces
                if (match := re.search(r"(\d+)$", row["piece_number"]))
            ),
            default=0,
        ) + 1
        hinted_piece = re.fullmatch(rf"{re.escape(prefix)}-(\d{{3,}})", request.piece_number_hint)
        if hinted_piece:
            piece_number = max(piece_number, int(hinted_piece.group(1)))
        piece = f"{prefix}-{piece_number:03d}"
        now = self._now()
        cursor = db.execute("INSERT INTO journal_entries(client_id, year, entry_number, piece_number, journal, entry_date, reference, label, user_id, posted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.client_id, request.year, number, piece, request.journal, request.entry_date, request.reference, request.label, request.user_id, now))
        new_id = int(cursor.lastrowid)
        for line_number, line in enumerate(request.lines, 1):
            db.execute("INSERT INTO journal_lines(entry_id, line_number, account_code, auxiliary_code, label, debit, credit, invoice, vat_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (new_id, line_number, line.account, line.auxiliary, line.label, line.debit, line.credit, line.invoice, line.vat_rate))
        payload = request.model_dump(by_alias=True, mode="json")
        payload.update({"entryId": new_id, "entryNumber": number, "pieceNumber": piece})
        for action in ("CREATE", "POST"):
            db.execute("INSERT INTO audit_logs(user_id, timestamp, action_type, entry_id, payload_diff) VALUES (?, ?, ?, ?, ?)", (request.user_id, now, action, new_id, json.dumps(payload, sort_keys=True)))
        return JournalEntryPosted(entryId=new_id, entryNumber=number, pieceNumber=piece, clientId=request.client_id, year=request.year)
