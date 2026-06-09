from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as books_router

app = FastAPI(
    title="Project Gutenberg Books API",
    description=(
        "A RESTful API to query and filter books from the Project Gutenberg dataset. "
        "Books are sorted by popularity (download count) and support pagination (25 per page). "
        "Filter by book IDs, languages, MIME types, topics, authors, and titles."
    ),
    version="1.0.0",
    contact={
        "name": "Gutenberg API",
        "url": "https://www.gutenberg.org/",
    },
    license_info={
        "name": "Project Gutenberg License",
        "url": "https://www.gutenberg.org/policy/license.html",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Allow cross-origin requests (needed for Render/frontend clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/", tags=["Root"])
def root():
    """API root — redirects to docs."""
    return {
        "message": "Welcome to the Project Gutenberg Books API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
