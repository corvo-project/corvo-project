from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ocr_indexer.database import SessionLocal
from ocr_indexer.models import Document, Page
from ocr_indexer.search import search_text
from fastapi import Depends

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
