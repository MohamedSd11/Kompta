"""
Wraps generated XML payloads in a project-defined ZIP archive.

The archive layout has not been verified against an official DGI
SIMPL transport specification or an accepted export.
"""
from __future__ import annotations

import io
import zipfile


def zip_xml_payload(xml_bytes: bytes, inner_filename: str) -> bytes:
    """
    Wrap a single XML document into an in-memory zip file and return
    the zip's raw bytes (ready to write to disk or stream as a download).
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(inner_filename, xml_bytes)
    return buffer.getvalue()
