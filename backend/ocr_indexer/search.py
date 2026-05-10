from sqlalchemy.orm import Session
from sqlalchemy.sql import text

def search_text(session: Session, query: str, page: int = 1, page_size: int = 25):
    safe_page = max(1, page)
    safe_page_size = max(1, page_size)
    offset = (safe_page - 1) * safe_page_size

    count_sql = text("""
        SELECT COUNT(*) AS total
        FROM pages_fts
        JOIN pages p ON p.id = pages_fts.rowid
        JOIN documents d ON d.id = p.document_id
        WHERE pages_fts.text_content MATCH :query
    """)

    sql = text("""
        SELECT d.id AS document_id, d.title, d.author,
               d.file_name, p.page_number, snippet(pages_fts, 0, '<b>', '</b>', '...', 10) AS snippet
        FROM pages_fts
        JOIN pages p ON p.id = pages_fts.rowid
        JOIN documents d ON d.id = p.document_id
        WHERE pages_fts.text_content MATCH :query
        LIMIT :limit
        OFFSET :offset
    """)
    total = session.execute(count_sql, {"query": query}).scalar() or 0
    results = session.execute(
        sql,
        {"query": query, "limit": safe_page_size, "offset": offset}
    ).fetchall()

    return {
        "total": total,
        "page": safe_page,
        "page_size": safe_page_size,
        "results": [
        {
            "document_id": row.document_id,
            "title": row.title,
            "author": row.author,
            "file_name": row.file_name,
            "page_number": row.page_number,
            "snippet": row.snippet
        }
        for row in results
        ]
    }
