from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

def search_advanced(
    session: Session,
    query: Optional[str] = None,
    event_ids: list = None,
    event_mode: str = "OR",
    toponym_ids: list = None,
    toponym_mode: str = "OR",
    page: int = 1,
    page_size: int = 25,
):
    safe_page = max(1, page)
    safe_page_size = max(1, min(100, page_size))
    offset = (safe_page - 1) * safe_page_size
    event_ids = event_ids or []
    toponym_ids = toponym_ids or []
    params: dict = {}
    ctes = []
    joins = []

    # CTE: pages matching the event filter
    if event_ids:
        e_ph = ", ".join(f":eid_{i}" for i in range(len(event_ids)))
        for i, eid in enumerate(event_ids):
            params[f"eid_{i}"] = eid
        if event_mode == "AND":
            params["n_events"] = len(event_ids)
            ctes.append(
                f"event_pages AS (SELECT page_id FROM events WHERE event_type IN ({e_ph})"
                f" GROUP BY page_id HAVING COUNT(DISTINCT event_type) = :n_events)"
            )
        else:
            ctes.append(
                f"event_pages AS (SELECT DISTINCT page_id FROM events WHERE event_type IN ({e_ph}))"
            )
        joins.append("JOIN event_pages ep ON ep.page_id = p.id")

    # CTE: pages matching the toponym filter (via all variants of each canonical toponym)
    if toponym_ids:
        t_ph = ", ".join(f":tid_{i}" for i in range(len(toponym_ids)))
        for i, tid in enumerate(toponym_ids):
            params[f"tid_{i}"] = tid
        if toponym_mode == "AND":
            params["n_toponyms"] = len(toponym_ids)
            ctes.append(
                f"toponym_pages AS ("
                f"SELECT tvp.page_id FROM toponym_variant_pages tvp"
                f" JOIN toponym_variants tv ON tv.id = tvp.toponym_variant_id"
                f" WHERE tv.toponym_id IN ({t_ph})"
                f" GROUP BY tvp.page_id HAVING COUNT(DISTINCT tv.toponym_id) = :n_toponyms)"
            )
        else:
            ctes.append(
                f"toponym_pages AS ("
                f"SELECT DISTINCT tvp.page_id FROM toponym_variant_pages tvp"
                f" JOIN toponym_variants tv ON tv.id = tvp.toponym_variant_id"
                f" WHERE tv.toponym_id IN ({t_ph}))"
            )
        joins.append("JOIN toponym_pages tp ON tp.page_id = p.id")

    cte_prefix = ("WITH " + ", ".join(ctes) + " ") if ctes else ""
    join_clause = " ".join(joins)

    if query and query.strip():
        params["query"] = '"' + query.strip().replace('"', '""') + '"'
        snippet_expr = "snippet(pages_fts, 0, '<b>', '</b>', '...', 10)"
        from_clause = "pages_fts JOIN pages p ON p.id = pages_fts.rowid JOIN documents d ON d.id = p.document_id"
        where_clause = "WHERE pages_fts.text_content MATCH :query"
    else:
        snippet_expr = "substr(p.text_content, 1, 300)"
        from_clause = "pages p JOIN documents d ON d.id = p.document_id"
        where_clause = ""

    count_sql = text(
        f"{cte_prefix}SELECT COUNT(*) FROM {from_clause} {join_clause} {where_clause}"
    )
    data_sql = text(
        f"{cte_prefix}SELECT d.id AS document_id, d.title, d.author, d.file_name,"
        f" p.page_number, {snippet_expr} AS snippet"
        f" FROM {from_clause} {join_clause} {where_clause}"
        f" LIMIT :limit OFFSET :offset"
    )

    total = session.execute(count_sql, params).scalar() or 0
    rows = session.execute(data_sql, {**params, "limit": safe_page_size, "offset": offset}).fetchall()

    return {
        "total": total,
        "page": safe_page,
        "page_size": safe_page_size,
        "results": [
            {"document_id": r.document_id, "title": r.title, "author": r.author,
             "file_name": r.file_name, "page_number": r.page_number, "snippet": r.snippet}
            for r in rows
        ],
    }

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
    fts_query = '"' + query.strip().replace('"', '""') + '"'
    total = session.execute(count_sql, {"query": fts_query}).scalar() or 0
    results = session.execute(
        sql,
        {"query": fts_query, "limit": safe_page_size, "offset": offset}
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
