import csv
import io
import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ocr_indexer.database import SessionLocal
from ocr_indexer.models import Document, Page, Event
from ocr_indexer.search import search_text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "author": doc.author,
            "total_pages": doc.total_pages
        } for doc in documents
    ]

@router.get("/documents/{document_id}/pages/{page_number}")
def get_page(document_id: int, page_number: int, db: Session = Depends(get_db)):
    page = (
        db.query(Page, Document)
        .join(Document, Page.document_id == Document.id)
        .filter(Page.document_id == document_id, Page.page_number == page_number)
        .first()
    )

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    page_data, document_data = page

    return {
        "document_id": document_id,
        "document_author": document_data.author,
        "document_title": document_data.title,
        "file_name": document_data.file_name,
        "page_number": page_data.page_number,
        "content": page_data.text_content
    }
@router.get("/search")
def search(q: str, page: int = 1, page_size: int = 25, db: Session = Depends(get_db)):
    return search_text(db, q, page=page, page_size=page_size)

def _normalize(name: str, strip_suffix: str) -> str:
    if name.endswith(strip_suffix):
        name = name[:-len(strip_suffix)]
    return re.sub(r'[^a-zA-Z0-9]', '', name)

def _build_doc_mapping(db: Session) -> dict[str, Document]:
    """Returns a dict: normalized CSV doc_name → Document."""
    docs = db.query(Document).all()
    db_map = {_normalize(doc.file_name, '.out'): doc for doc in docs}

    mapping = {}
    for db_norm, doc in db_map.items():
        # Precompute: for any CSV name that contains db_norm as substring → this doc
        mapping[db_norm] = (doc, 'db_in_csv')

    return db_map

def _resolve_doc(csv_doc_name: str, db_map: dict) -> Document | None:
    csv_norm = _normalize(csv_doc_name, '.pdf')
    # 1) db_norm is substring of csv_norm
    for db_norm, doc in db_map.items():
        if db_norm and db_norm in csv_norm:
            return doc
    # 2) csv_norm is substring of db_norm
    for db_norm, doc in db_map.items():
        if csv_norm and csv_norm in db_norm:
            return doc
    return None

@router.post("/import/events")
async def import_events(file: UploadFile = File(...), clear: bool = False, max_warnings: int = 100, db: Session = Depends(get_db)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    if clear:
        deleted = db.query(Event).delete()
        db.commit()
        print(f"[import] Cleared {deleted} existing events", flush=True)

    db_map = _build_doc_mapping(db)
    print(f"[import] Loaded {len(db_map)} documents from DB", flush=True)

    warnings = []
    total_warnings = 0
    imported = 0
    doc_cache: dict[str, Document | None] = {}
    page_cache: dict[tuple, Page | None] = {}

    for line_number, row in enumerate(reader, start=2):  # row 1 is the header
        event_id = int(row["event_id"])
        if event_id == -1:
            continue

        csv_doc_name = row["doc_name"]
        if csv_doc_name not in doc_cache:
            doc_cache[csv_doc_name] = _resolve_doc(csv_doc_name, db_map)
        doc = doc_cache[csv_doc_name]
        if doc is None:
            total_warnings += 1
            msg = f"[line {line_number}] Document not found: '{csv_doc_name}'"
            print(msg, flush=True)
            if len(warnings) < max_warnings:
                warnings.append({"line": line_number, "message": f"Document not found: '{csv_doc_name}'"})
            continue

        page_number = int(row["page"])
        cache_key = (doc.id, page_number)
        if cache_key not in page_cache:
            page = db.query(Page).filter(
                Page.document_id == doc.id,
                Page.page_number == page_number
            ).first()
            page_cache[cache_key] = page
        page = page_cache[cache_key]
        if page is None:
            total_warnings += 1
            msg = f"[line {line_number}] Page {page_number} not found in document '{csv_doc_name}'"
            print(msg, flush=True)
            if len(warnings) < max_warnings:
                warnings.append({"line": line_number, "message": f"Page {page_number} not found in document '{csv_doc_name}'"})
            continue

        event = Event(
            page_id=page.id,
            offset=int(row["offset"]),
            term=row["termine"],
            event_type=event_id,
            sentence=row["sentence"],
        )
        db.add(event)
        imported += 1

    db.commit()
    print(f"[import] Done: {imported} imported, {total_warnings} warnings", flush=True)
    return {"imported": imported, "total_warnings": total_warnings, "warnings": warnings}
