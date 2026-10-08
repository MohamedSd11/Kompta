"""
Pre-flight XSD validator.

Validates generated XML against an XSD schema file before it is allowed
to be zipped/downloaded, and returns a diagnostic report with line
numbers and the failing XML node/path - not just a boolean.

Requires `lxml` (pip install lxml).

NOTE: Ship the *real* DGI XSD files under core/schemas/ once obtained;
the placeholder schemas in this repo only encode the tag shape implied
by the feature spec and are NOT a substitute for the official schema.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lxml import etree


@dataclass
class XsdDiagnostic:
    line: int
    column: int
    message: str
    path: str | None = None


@dataclass
class XsdValidationResult:
    valid: bool
    diagnostics: list[XsdDiagnostic]

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "diagnostics": [
                {"line": d.line, "column": d.column, "message": d.message, "path": d.path}
                for d in self.diagnostics
            ],
        }


class XsdValidator:
    def __init__(self, xsd_path: str | Path):
        self.xsd_path = Path(xsd_path)
        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD schema not found: {self.xsd_path}")
        with open(self.xsd_path, "rb") as f:
            schema_doc = etree.parse(f)
        self._schema = etree.XMLSchema(schema_doc)

    def validate(self, xml_bytes: bytes) -> XsdValidationResult:
        try:
            doc = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as e:
            return XsdValidationResult(
                valid=False,
                diagnostics=[XsdDiagnostic(line=e.lineno or 0, column=e.offset or 0, message=str(e))],
            )

        is_valid = self._schema.validate(doc)
        diagnostics: list[XsdDiagnostic] = []
        if not is_valid:
            for err in self._schema.error_log:
                diagnostics.append(
                    XsdDiagnostic(
                        line=err.line,
                        column=err.column,
                        message=err.message,
                        path=getattr(err, "path", None),
                    )
                )
        return XsdValidationResult(valid=is_valid, diagnostics=diagnostics)


def validate_against_schema(xml_bytes: bytes, xsd_path: str | Path) -> XsdValidationResult:
    """Convenience one-shot validation call."""
    validator = XsdValidator(xsd_path)
    return validator.validate(xml_bytes)
