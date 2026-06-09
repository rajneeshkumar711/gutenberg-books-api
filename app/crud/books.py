from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Book, Author, Language, Format, Subject, Bookshelf

PAGE_SIZE = 25


def get_books(
    db: Session,
    page: int = 1,
    book_ids: Optional[str] = None,
    languages: Optional[str] = None,
    mime_types: Optional[str] = None,
    topic: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None,
):
    # Start with a subquery that collects matching book IDs with dedup
    id_query = db.query(Book.id)

    # ── Filter: specific gutenberg IDs (comma-separated) ──────────────────────
    if book_ids:
        ids = [i.strip() for i in book_ids.split(",") if i.strip().isdigit()]
        if ids:
            id_query = id_query.filter(Book.gutenberg_id.in_([int(i) for i in ids]))

    # ── Filter: language codes (comma-separated, e.g. "en,fr") ───────────────
    if languages:
        lang_list = [l.strip() for l in languages.split(",") if l.strip()]
        id_query = (
            id_query.join(Book.languages)
            .filter(Language.code.in_(lang_list))
        )

    # ── Filter: mime-type (comma-separated) ───────────────────────────────────
    if mime_types:
        mime_list = [m.strip() for m in mime_types.split(",") if m.strip()]
        id_query = (
            id_query.join(Book.formats)
            .filter(or_(*[Format.mime_type.ilike(f"%{m}%") for m in mime_list]))
        )

    # ── Filter: topic – searches subjects AND bookshelves (case-insensitive) ──
    if topic:
        topics = [t.strip() for t in topic.split(",") if t.strip()]
        topic_filters = []
        for t in topics:
            subject_ids = db.query(Book.id).join(Book.subjects).filter(Subject.name.ilike(f"%{t}%"))
            shelf_ids = db.query(Book.id).join(Book.bookshelves).filter(Bookshelf.name.ilike(f"%{t}%"))
            combined = subject_ids.union(shelf_ids).subquery()
            topic_filters.append(Book.id.in_(select(combined)))
        id_query = id_query.filter(or_(*topic_filters))

    # ── Filter: author name (case-insensitive partial match) ──────────────────
    if author:
        author_terms = [a.strip() for a in author.split(",") if a.strip()]
        id_query = (
            id_query.join(Book.authors)
            .filter(or_(*[Author.name.ilike(f"%{a}%") for a in author_terms]))
        )

    # ── Filter: title (case-insensitive partial match) ────────────────────────
    if title:
        title_terms = [t.strip() for t in title.split(",") if t.strip()]
        id_query = id_query.filter(
            or_(*[Book.title.ilike(f"%{t}%") for t in title_terms])
        )

    # Deduplicate matched IDs
    matching_ids_subquery = id_query.distinct().subquery()

    # ── Count total matching books ────────────────────────────────────────────
    total = db.query(Book).filter(Book.id.in_(select(matching_ids_subquery))).count()

    # ── Fetch page of books with all relationships ─────────────────────────────
    offset = (page - 1) * PAGE_SIZE
    books = (
        db.query(Book)
        .filter(Book.id.in_(select(matching_ids_subquery)))
        .order_by(Book.download_count.desc().nullslast())
        .offset(offset)
        .limit(PAGE_SIZE)
        .all()
    )

    return total, books
