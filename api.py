"""
FastAPI routes for the DGI SIMPL EDI/XML Export Engine.

POST /api/exports/simpl-tva   -> validate + build + zip the Relevé des Déductions
POST /api/exports/simpl-ir    -> validate + build + zip the État 9421

On business-rule or XSD failure, returns HTTP 422 with a structured
diagnostic report (line numbers, failing field/node, message).
On success, returns HTTP 200 with the zip file as an attachment.
"""
from __future__ import annotations

import io
import sqlite3

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from core.excel_export import build_portfolio_tva_excel, build_tva_excel
from core.export_safety import require_demo_export, safety_download_headers
from core.export_service import export_etat_9421, export_releve_deductions
from core.liasse_models import LiasseComputeRequest
from core.liasse_service import build_simpl_is_xml, compute_liasse, validate_simpl_is_xml
from core.models import Etat9421, ExcelExportRequest, PortfolioExcelRequest, ReleveDeductions
from core.journal_service import JournalEntryPost, JournalEntryPosted, JournalRepository
from core.client_service import ClientRepository, ClientUpsert, FiscalYearUpsert
from core.ocr_service import OcrDocumentStore


journal_repository = JournalRepository()
client_repository = ClientRepository()
ocr_store = OcrDocumentStore()

router = APIRouter(prefix="/api/exports", tags=["dgi-exports"])
clients_router = APIRouter(prefix="/api/clients", tags=["clients"])
accounts_router = APIRouter(prefix="/api/accounts", tags=["accounts"])

ocr_router = APIRouter(prefix="/api/ocr", tags=["ocr"])
LOCAL_ACTOR = "local-owner"


@clients_router.get("")
def list_clients(include_demo: bool = True):
    return client_repository.list_clients(include_demo=include_demo)


@clients_router.post("")
def create_client(request: ClientUpsert):
    try:
        return client_repository.create_client(request)
    except (sqlite3.IntegrityError, ValueError) as error:
        raise HTTPException(status_code=409, detail={"message": "Un client réel avec cet ICE existe déjà"}) from error


@clients_router.put("/{client_id}")
def update_client(client_id: str, request: ClientUpsert):
    try:
        return client_repository.update_client(client_id, request)
    except KeyError as error:
        raise HTTPException(status_code=404, detail={"message": "Client réel introuvable"}) from error
    except (sqlite3.IntegrityError, ValueError) as error:
        raise HTTPException(status_code=409, detail={"message": "Un client réel avec cet ICE existe déjà"}) from error


@clients_router.post("/{client_id}/fiscal-years")
def save_fiscal_year(client_id: str, request: FiscalYearUpsert):
    try:
        return client_repository.save_fiscal_year(client_id, request)
    except KeyError as error:
        raise HTTPException(status_code=404, detail={"message": "Client réel introuvable"}) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"message": str(error)}) from error


@accounts_router.get("/pcge-general/preview")
def preview_pcge_general_accounts():
    try:
        return journal_repository.preview_pcge_general()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail={"message": str(error)}) from error


@accounts_router.post("/pcge-general/preview")
def preview_pcge_general_accounts_with_catalog(request: dict[str, object]):
    try:
        catalog = request.get("accountCatalog", [])
        return journal_repository.preview_pcge_general(existing=catalog if isinstance(catalog, list) else [])
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail={"message": str(error)}) from error


@accounts_router.post("/pcge-general/import")
def import_pcge_general_accounts(request: dict[str, object]):
    try:
        catalog = request.get("accountCatalog", [])
        return journal_repository.import_pcge_general(existing=catalog if isinstance(catalog, list) else [])
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=503, detail={"message": str(error)}) from error


@ocr_router.post("/documents")
async def upload_ocr_document(
    request: Request,
):
    """Retain a validated source document for review; OCR is never posted automatically."""
    try:
        client_id = request.headers.get("x-kompta-client-id", "")
        year = int(request.headers.get("x-kompta-year", "0"))
        filename = request.headers.get("x-kompta-filename", "")
        mime_type = request.headers.get("content-type", "")
        client_ice = request.headers.get("x-kompta-client-ice")
        content = await request.body()
        return ocr_store.upload(client_id, year, filename, mime_type, content, active_client_ice=client_ice)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail={"message": str(error)}) from error


@ocr_router.get("/documents/{document_id}")
def get_ocr_document(document_id: int, client_id: str, year: int):
    document = ocr_store.get(document_id, client_id, year)
    if document is None:
        raise HTTPException(status_code=404, detail={"message": "Document OCR introuvable"})
    return document


@router.post("/journal-entries", response_model=JournalEntryPosted)
def post_journal_entry(request: JournalEntryPost):
    """Post one balanced entry; numbering is allocated inside the DB lock."""
    try:
        return journal_repository.post(request.model_copy(update={"user_id": LOCAL_ACTOR}))
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"message": str(error)}) from error


def list_journal_entries(client_id: str, year: int):
    """Read only entries matching the active local dossier and fiscal year."""
    return journal_repository.list_entries(client_id, year)


@router.post("/journal-entries/{entry_id}/reversal", response_model=JournalEntryPosted)
def reverse_journal_entry(entry_id: int, client_id: str, year: int):
    """Create a standard contre-passation; the original is never edited."""
    try:
        return journal_repository.reverse(
            entry_id, LOCAL_ACTOR, expected_client_id=client_id, expected_year=year
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"message": str(error)}) from error


@router.post("/liasse/compute")
def compute_liasse_endpoint(request: LiasseComputeRequest):
    return compute_liasse(request)


@router.post("/liasse/simpl-is.xml")
def export_simpl_is(request: LiasseComputeRequest):
    require_demo_export(request.demo_only)
    result = compute_liasse(request)
    xml_bytes = build_simpl_is_xml(result)
    valid, diagnostics = validate_simpl_is_xml(xml_bytes)
    if not valid:
        raise HTTPException(status_code=422, detail={"message": "SIMPL-IS XML invalide", "diagnostics": diagnostics})
    return StreamingResponse(
        io.BytesIO(xml_bytes), media_type="application/xml",
        headers=safety_download_headers(f"SIMPL_IS_{request.fiscal_year}.xml"),
    )


@router.post("/simpl-tva")
def export_simpl_tva(releve: ReleveDeductions):
    require_demo_export(releve.demo_only)
    outcome = export_releve_deductions(releve)
    if not outcome.success:
        raise HTTPException(status_code=422, detail=outcome.to_dict())

    return StreamingResponse(
        io.BytesIO(outcome.zip_bytes),
        media_type="application/zip",
        headers=safety_download_headers(outcome.zip_filename),
    )


@router.post("/export-excel")
@router.post("/tva-excel")
@router.post("/export-tva-excel")
def export_tva_excel(request: ExcelExportRequest):
    workbook_bytes = build_tva_excel(request)
    filename = f"TVA_{request.releve.periode}.xlsx"
    return StreamingResponse(
        io.BytesIO(workbook_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export-portfolio-tva-excel")
def export_portfolio_tva_excel(request: PortfolioExcelRequest):
    workbook_bytes = build_portfolio_tva_excel(request)
    return StreamingResponse(
        io.BytesIO(workbook_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Recapitulatif_TVA_Portefeuille.xlsx"'},
    )


@router.post("/simpl-ir")
def export_simpl_ir(etat: Etat9421):
    require_demo_export(etat.demo_only)
    outcome = export_etat_9421(etat)
    if not outcome.success:
        raise HTTPException(status_code=422, detail=outcome.to_dict())

    return StreamingResponse(
        io.BytesIO(outcome.zip_bytes),
        media_type="application/zip",
        headers=safety_download_headers(outcome.zip_filename),
    )


@router.post("/simpl-tva/validate")
def validate_simpl_tva(releve: ReleveDeductions):
    """Dry-run: run business validation only, without generating XML/zip."""
    from core.validators import validate_releve_deductions

    report = validate_releve_deductions(releve)
    return report.to_dict()


@router.post("/simpl-ir/validate")
def validate_simpl_ir(etat: Etat9421):
    """Dry-run: run business validation only, without generating XML/zip."""
    from core.validators import validate_etat_9421

    report = validate_etat_9421(etat)
    return report.to_dict()
