from typing import Optional
from pydantic import BaseModel


class AuthorSchema(BaseModel):
    name: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None

    model_config = {"from_attributes": True}


class FormatSchema(BaseModel):
    mime_type: str
    url: str

    model_config = {"from_attributes": True}


class BookSchema(BaseModel):
    id: int
    gutenberg_id: int
    title: Optional[str] = None
    media_type: str
    download_count: Optional[int] = None
    authors: list[AuthorSchema] = []
    languages: list[str] = []
    subjects: list[str] = []
    bookshelves: list[str] = []
    formats: list[FormatSchema] = []

    model_config = {"from_attributes": True}


class PaginatedBooksResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[BookSchema]
