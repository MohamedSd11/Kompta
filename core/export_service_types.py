from __future__ import annotations

from dataclasses import dataclass

from .validators import ValidationReport
from .xsd_validator import XsdValidationResult


@dataclass
class ExportOutcome:
    success: bool
    business_report: ValidationReport | None = None
    xsd_result: XsdValidationResult | None = None
    xml_bytes: bytes | None = None
    zip_bytes: bytes | None = None
    zip_filename: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "business_validation": self.business_report.to_dict() if self.business_report else None,
            "xsd_validation": self.xsd_result.to_dict() if self.xsd_result else None,
            "zip_filename": self.zip_filename,
        }
