from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association tables (many-to-many)
book_authors = Table(
    "books_book_authors",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books_book.id")),
    Column("author_id", Integer, ForeignKey("books_author.id")),
)

book_languages = Table(
    "books_book_languages",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books_book.id")),
    Column("language_id", Integer, ForeignKey("books_language.id")),
)

book_subjects = Table(
    "books_book_subjects",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books_book.id")),
    Column("subject_id", Integer, ForeignKey("books_subject.id")),
)

book_bookshelves = Table(
    "books_book_bookshelves",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books_book.id")),
    Column("bookshelf_id", Integer, ForeignKey("books_bookshelf.id")),
)


class Book(Base):
    __tablename__ = "books_book"

    id = Column(Integer, primary_key=True, index=True)
    gutenberg_id = Column(Integer, unique=True, nullable=False)
    title = Column(String(1024), nullable=True)
    media_type = Column(String(16), nullable=False)
    download_count = Column(Integer, nullable=True)

    authors = relationship("Author", secondary=book_authors, lazy="joined")
    languages = relationship("Language", secondary=book_languages, lazy="joined")
    subjects = relationship("Subject", secondary=book_subjects, lazy="joined")
    bookshelves = relationship("Bookshelf", secondary=book_bookshelves, lazy="joined")
    formats = relationship("Format", back_populates="book", lazy="joined")


class Author(Base):
    __tablename__ = "books_author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    birth_year = Column(SmallInteger, nullable=True)
    death_year = Column(SmallInteger, nullable=True)


class Language(Base):
    __tablename__ = "books_language"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(4), unique=True, nullable=False)


class Subject(Base):
    __tablename__ = "books_subject"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)


class Bookshelf(Base):
    __tablename__ = "books_bookshelf"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)


class Format(Base):
    __tablename__ = "books_format"

    id = Column(Integer, primary_key=True, index=True)
    mime_type = Column(String(32), nullable=False)
    url = Column(String(256), nullable=False)
    book_id = Column(Integer, ForeignKey("books_book.id"), nullable=False)

    book = relationship("Book", back_populates="formats")
