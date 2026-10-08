"""Source-backed import of the general-business PCGE chart.

The supplied PCGE PDF is the source of labels and codes. Classes 1-8 are the
general-business chart; classes 0 and 9 are deliberately left outside this
import because they are special/analytical accounts.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader


DEFAULT_PCGE_SOURCE = Path.home() / "Downloads" / "Plan-Comptable-Marocain-Upsilon-Consulting.pdf"
ACCOUNT_CODE = re.compile(r"^[0-9]{2,5}$")
CLASS_HEADING = re.compile(r"^Classe\s+([1-8])$")


def resolve_pcge_source(path: str | Path | None = None) -> Path:
    configured = path or os.environ.get("KOMPTA_PCGE_SOURCE_PDF") or DEFAULT_PCGE_SOURCE
    source = Path(configured).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"PCGE source PDF not found: {source}")
    return source


def parse_pcge_text(text: str) -> list[dict[str, Any]]:
    """Parse code/label pairs without altering source labels."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    accounts: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    current_class: str | None = None

    for index, line in enumerate(lines[:-1]):
        class_match = CLASS_HEADING.fullmatch(line)
        if class_match:
            current_class = class_match.group(1)
            continue
        if not current_class or not ACCOUNT_CODE.fullmatch(line) or not line.startswith(current_class):
            continue
        label = lines[index + 1]
        if not label or ACCOUNT_CODE.fullmatch(label) or label.startswith(("UPSILON", "Plan Comptable", "Page ")):
            continue
        candidate = {"code": line, "label": label, "class": int(current_class), "source": "pcge_general"}
        previous = accounts.get(line)
        if previous and previous["label"] != label:
            conflicts.append({"code": line, "labels": [previous["label"], label], "reason": "duplicate_source_code"})
        else:
            accounts.setdefault(line, candidate)

    for conflict in conflicts:
        accounts[conflict["code"]]["needs_review"] = True
        accounts[conflict["code"]]["review_reason"] = conflict["reason"]
    for account in accounts.values():
        if "\ufffd" in account["label"]:
            account["needs_review"] = True
            account["review_reason"] = "source_text_encoding"

    return sorted(accounts.values(), key=lambda item: (item["class"], item["code"]))


def extract_pcge_general_accounts(path: str | Path | None = None) -> list[dict[str, Any]]:
    source = resolve_pcge_source(path)
    text = "\n".join(page.extract_text() or "" for page in PdfReader(source).pages)
    return parse_pcge_text(text)


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
