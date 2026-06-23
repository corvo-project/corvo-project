import csv
import io
import json
import os
import re
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ocr_indexer.database import SessionLocal
from ocr_indexer.models import Document, Page, Event, EventDescription, Toponym, ToponymVariant, toponym_variant_pages
from ocr_indexer.search import search_text

router = APIRouter()

_bearer_scheme = HTTPBearer(auto_error=False)

def require_bearer_token(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> None:
    if request.method == "OPTIONS":
        return
    api_token = os.getenv("API_BEARER_TOKEN")
    if not api_token:
        raise HTTPException(status_code=500, detail="API_BEARER_TOKEN not configured")
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    if creds.credentials != api_token:
        raise HTTPException(status_code=403, detail="Invalid token")

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

    events = (
        db.query(Event, EventDescription)
        .join(EventDescription, Event.event_type == EventDescription.id)
        .filter(Event.page_id == page_data.id)
        .all()
    )

    toponyms = (
        db.query(ToponymVariant, Toponym)
        .join(Toponym, ToponymVariant.toponym_id == Toponym.id)
        .join(toponym_variant_pages, toponym_variant_pages.c.toponym_variant_id == ToponymVariant.id)
        .filter(toponym_variant_pages.c.page_id == page_data.id)
        .all()
    )
    seen_toponym_ids = set()
    toponyms_list = []
    for variant, toponym in toponyms:
        if toponym.id not in seen_toponym_ids:
            seen_toponym_ids.add(toponym.id)
            toponyms_list.append({
                "name": toponym.name,
                "type": toponym.type,
                "location_info": toponym.location_info,
            })

    return {
        "document_id": document_id,
        "document_author": document_data.author,
        "document_title": document_data.title,
        "file_name": document_data.file_name,
        "page_number": page_data.page_number,
        "content": page_data.text_content,
        "events": _deduplicate_events(events),
        "toponyms": toponyms_list,
    }
@router.get("/search")
def search(q: str, page: int = 1, page_size: int = 25, db: Session = Depends(get_db)):
    return search_text(db, q, page=page, page_size=page_size)

def _deduplicate_events(events):
    seen = set()
    result = []
    for ev, desc in events:
        key = (ev.event_type, ev.offset)
        if key not in seen:
            seen.add(key)
            result.append({"event_type": desc.description, "sentence": ev.sentence})
    return result

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
async def import_events(file: UploadFile = File(...), clear: bool = False, max_warnings: int = 100, db: Session = Depends(get_db), _: None = Depends(require_bearer_token)):
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


def _link_variants_to_pages(variant_ids_and_names: list[tuple[int, str]]) -> None:
    db = SessionLocal()
    try:
        pages = db.query(Page.id, Page.text_content).all()
        total = len(variant_ids_and_names)
        milestone = max(1, total // 10)
        links_inserted = 0

        for i, (variant_id, name) in enumerate(variant_ids_and_names):
            for page_id, text_content in pages:
                if text_content and name in text_content:
                    db.execute(
                        toponym_variant_pages.insert().values(
                            toponym_variant_id=variant_id,
                            page_id=page_id,
                        )
                    )
                    links_inserted += 1

            if (i + 1) % milestone == 0 or i + 1 == total:
                pct = round((i + 1) / total * 100)
                print(f"[toponyms] {pct}% ({i + 1}/{total} variants processed, {links_inserted} links so far)", flush=True)

        db.commit()
        print(f"[toponyms] Background task complete: {links_inserted} total links inserted", flush=True)
    except Exception as e:
        db.rollback()
        print(f"[toponyms] Background task error: {e}", flush=True)
    finally:
        db.close()


@router.post("/import/toponyms")
async def import_toponyms(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    clear: bool = False,
    db: Session = Depends(get_db),
    _: None = Depends(require_bearer_token),
):
    content = await file.read()
    locations = json.loads(content.decode("utf-8"))

    if clear:
        db.execute(toponym_variant_pages.delete())
        db.query(ToponymVariant).delete()
        db.query(Toponym).delete()
        db.commit()
        print("[toponyms] Cleared existing toponyms, variants and links", flush=True)

    toponym_count = 0
    variant_ids_and_names: list[tuple[int, str]] = []

    for loc in locations:
        location_info = loc.get("location_info")
        toponym = Toponym(
            name=loc["name"],
            type=loc["type"],
            location_info=json.dumps(location_info, ensure_ascii=False) if location_info else None,
        )
        db.add(toponym)
        db.flush()

        names = list(dict.fromkeys([loc["name"]] + loc.get("alternate_names", [])))
        for name in names:
            variant = ToponymVariant(name=name, toponym_id=toponym.id)
            db.add(variant)
            db.flush()
            variant_ids_and_names.append((variant.id, name))

        toponym_count += 1

    db.commit()
    print(f"[toponyms] Inserted {toponym_count} toponyms, {len(variant_ids_and_names)} variants — starting background search", flush=True)

    background_tasks.add_task(_link_variants_to_pages, variant_ids_and_names)

    return {
        "toponyms_imported": toponym_count,
        "variants_created": len(variant_ids_and_names),
        "status": "text search running in background",
    }
