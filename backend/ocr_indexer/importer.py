import json
import os
from .database import SessionLocal, engine
from .models import Base, Document, Page

Base.metadata.create_all(bind=engine)

def import_document(title, author, folder_path):
    session = SessionLocal()
    try:
        file_name = os.path.basename(folder_path)
        existing = session.query(Document).filter_by(file_name=file_name).first()
        if existing:
            print(f"Document already imported: {file_name}")
            return

        jpg_files = sorted([
            f for f in os.listdir(folder_path) if f.endswith(".jpg")
        ])
        total_pages = len(jpg_files)
        document = Document(title=title, author=author, file_name=file_name, total_pages=total_pages)
        session.add(document)
        session.commit()

        for idx, filename in enumerate(jpg_files):
            filename = filename.replace(".jpg", ".pdf.json")
            content = ""
            file_path = os.path.join(folder_path, filename)
            if os.path.exists(file_path):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    json_content = json.load(f)
                    content = json_content['text'] if 'text' in json_content else ""
            page = Page(document_id=document.id, page_number=idx + 1, text_content=content)
            session.add(page)

        session.commit()
        print(f"Imported document: {title} with {total_pages} pages.")
    except Exception as e:
        print("Import failed:", e)
        session.rollback()
    finally:
        session.close()
