from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.crud import get_books, PAGE_SIZE
from app.core.database import get_db
from app.schemas import BookSchema, PaginatedBooksResponse

router = APIRouter(prefix="/books", tags=["Books"])


def _build_book_schema(book) -> BookSchema:
    return BookSchema(
        id=book.id,
        gutenberg_id=book.gutenberg_id,
        title=book.title,
        media_type=book.media_type,
        download_count=book.download_count,
        authors=[
            {"name": a.name, "birth_year": a.birth_year, "death_year": a.death_year}
            for a in book.authors
        ],
        languages=[lang.code for lang in book.languages],
        subjects=[s.name for s in book.subjects],
        bookshelves=[b.name for b in book.bookshelves],
        formats=[{"mime_type": f.mime_type, "url": f.url} for f in book.formats],
    )


@router.get(
    "",
    response_model=PaginatedBooksResponse,
    summary="List Books",
    description=(
        "Retrieve a paginated list of books from the Project Gutenberg dataset. "
        "Books are returned in descending order of popularity (download count). "
        "Supports multiple comma-separated values for all filter parameters."
    ),
)
def list_books(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    book_ids: Optional[str] = Query(
        None,
        alias="ids",
        description="Comma-separated Project Gutenberg IDs (e.g. `1,2,84`)",
    ),
    languages: Optional[str] = Query(
        None,
        alias="languages",
        description="Comma-separated language codes (e.g. `en,fr`)",
    ),
    mime_types: Optional[str] = Query(
        None,
        alias="mime_type",
        description="Comma-separated MIME types (e.g. `application/epub+zip,text/html`)",
    ),
    topic: Optional[str] = Query(
        None,
        description="Comma-separated topic keywords — matches subjects and bookshelves (e.g. `child,history`)",
    ),
    author: Optional[str] = Query(
        None,
        description="Comma-separated author name keywords — case-insensitive partial match (e.g. `dickens`)",
    ),
    title: Optional[str] = Query(
        None,
        description="Comma-separated title keywords — case-insensitive partial match (e.g. `adventures`)",
    ),
    db: Session = Depends(get_db),
):
    total, books = get_books(
        db=db,
        page=page,
        book_ids=book_ids,
        languages=languages,
        mime_types=mime_types,
        topic=topic,
        author=author,
        title=title,
    )

    base_url = str(request.url).split("?")[0]
    params = dict(request.query_params)

    def build_page_url(p: int) -> str:
        params["page"] = str(p)
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?{qs}"

    has_next = (page * PAGE_SIZE) < total
    has_prev = page > 1

    return PaginatedBooksResponse(
        count=total,
        next=build_page_url(page + 1) if has_next else None,
        previous=build_page_url(page - 1) if has_prev else None,
        results=[_build_book_schema(b) for b in books],
    )
