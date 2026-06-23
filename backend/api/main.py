from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import router
from ocr_indexer.database import SessionLocal
from sqlalchemy import text

app = FastAPI(title="OCR Document API")

app.include_router(router)

@app.on_event("startup")
def create_search_indexes():
    db = SessionLocal()
    try:
        for stmt in [
            "CREATE INDEX IF NOT EXISTS idx_events_page_id ON events(page_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_tvp_page_id ON toponym_variant_pages(page_id)",
            "CREATE INDEX IF NOT EXISTS ix_toponym_variants_toponym_id ON toponym_variants(toponym_id)",
        ]:
            db.execute(text(stmt))
        db.commit()
    finally:
        db.close()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# app.mount("/static", StaticFiles(directory="/home/alessio/corvo/backend/data/documents"), name="static")
