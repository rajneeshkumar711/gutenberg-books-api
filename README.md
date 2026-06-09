# Project Gutenberg Books API

A RESTful API to query and filter books from the [Project Gutenberg](https://www.gutenberg.org/) dataset.
Books are sorted by popularity (download count) and paginated at 25 per page.

[![CI](https://github.com/rajneeshkumar711/gutenberg-books-api/actions/workflows/ci.yml/badge.svg)](https://github.com/rajneeshkumar711/gutenberg-books-api/actions/workflows/ci.yml)

---

## Live Demo

| Endpoint | URL |
|---|---|
| Swagger UI (interactive docs) | `https://gutenberg-books-api.onrender.com/docs` |
| ReDoc | `https://gutenberg-books-api.onrender.com/redoc` |
| Health check | `https://gutenberg-books-api.onrender.com/health` |
| Books API | `https://gutenberg-books-api.onrender.com/books` |

---

## Tech Stack

- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (Project Gutenberg / Gutendex dump)
- **ORM:** SQLAlchemy 2.0
- **Hosting:** Render (PaaS)
- **CI/CD:** GitHub Actions

---

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app + middleware
│   ├── core/
│   │   ├── config.py        # Settings (loaded from .env)
│   │   └── database.py      # DB engine, session, Base
│   ├── models/
│   │   └── book.py          # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── book.py          # Pydantic response schemas
│   ├── crud/
│   │   └── books.py         # Query / filter logic
│   └── routes/
│       └── books.py         # GET /books endpoint
├── tests/
│   └── test_api.py          # 11 API integration tests
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI
├── Dockerfile
├── docker-compose.yml
├── render.yaml              # Render deploy config (prod + dev)
├── requirements.txt
├── .env.example             # Safe template — copy to .env
└── DEPLOY.md                # Render deployment guide
```

---

## Local Setup

### 1. Clone & create virtual environment

```bash
git clone https://github.com/rajneeshkumar711/gutenberg-books-api.git
cd gutenberg-books-api
python -m venv myenv
myenv\Scripts\activate        # Windows
# source myenv/bin/activate   # macOS / Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL connection string:

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
HOST=0.0.0.0
PORT=8000
```

### 4. Load the database dump

```bash
pg_restore --no-owner -d "postgresql://USER:PASSWORD@HOST:5432/DBNAME" gutendex.dump
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

API is now live at **http://localhost:8000**

---

## API Reference

### `GET /books`

Returns a paginated list of books sorted by download count (most popular first).

#### Query Parameters

| Parameter | Alias | Type | Description | Example |
|-----------|-------|------|-------------|---------|
| `page` | — | integer | Page number (default: 1) | `?page=2` |
| `ids` | — | string | Comma-separated Gutenberg IDs | `?ids=1,2,84` |
| `languages` | — | string | Comma-separated language codes | `?languages=en,fr` |
| `mime_type` | — | string | Comma-separated MIME types (partial match) | `?mime_type=text/html` |
| `topic` | — | string | Searches both subjects AND bookshelves (case-insensitive partial) | `?topic=child` |
| `author` | — | string | Author name (case-insensitive partial) | `?author=dickens` |
| `title` | — | string | Book title (case-insensitive partial) | `?title=adventures` |

#### Response Format

```json
{
  "count": 1234,
  "next": "http://localhost:8000/books?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "gutenberg_id": 84,
      "title": "Frankenstein; Or, The Modern Prometheus",
      "media_type": "Text",
      "download_count": 78890,
      "authors": [
        { "name": "Shelley, Mary Wollstonecraft", "birth_year": 1797, "death_year": 1851 }
      ],
      "languages": ["en"],
      "subjects": ["Horror tales", "Science fiction"],
      "bookshelves": ["Gothic Fiction"],
      "formats": [
        { "mime_type": "text/html", "url": "https://www.gutenberg.org/files/84/84-h/84-h.htm" },
        { "mime_type": "application/epub+zip", "url": "https://www.gutenberg.org/ebooks/84.epub3.images" }
      ]
    }
  ]
}
```

---

## Testing the API — All Filter Examples

### Using Swagger UI (easiest)
Open **http://localhost:8000/docs** → click `GET /books` → click **Try it out** → fill in parameters → **Execute**.

### Using curl

```bash
# 1. All books (default — page 1, sorted by popularity)
curl "http://localhost:8000/books"

# 2. Specific books by Gutenberg ID
curl "http://localhost:8000/books?ids=11,12,84"

# 3. Filter by single language
curl "http://localhost:8000/books?languages=en"

# 4. Filter by multiple languages (comma-separated)
curl "http://localhost:8000/books?languages=en,fr"

# 5. Filter by MIME type (partial match)
curl "http://localhost:8000/books?mime_type=text/html"

# 6. Filter by multiple MIME types
curl "http://localhost:8000/books?mime_type=application/epub%2Bzip,text/html"

# 7. Topic filter — matches subjects AND bookshelves
curl "http://localhost:8000/books?topic=child"
curl "http://localhost:8000/books?topic=child,infant"

# 8. Author filter (case-insensitive partial match)
curl "http://localhost:8000/books?author=shakespeare"
curl "http://localhost:8000/books?author=dickens,twain"

# 9. Title filter (case-insensitive partial match)
curl "http://localhost:8000/books?title=romeo"
curl "http://localhost:8000/books?title=adventures,island"

# 10. Multiple filters combined
curl "http://localhost:8000/books?languages=en&topic=drama&author=shakespeare"

# 11. Pagination — get page 2
curl "http://localhost:8000/books?page=2"

# 12. Combined filters with pagination
curl "http://localhost:8000/books?languages=en&author=dickens&page=2"
```

### Using Python requests

```python
import requests

BASE = "http://localhost:8000"

# All books
r = requests.get(f"{BASE}/books")
print(r.json()["count"], "total books")

# Filter by author + language
r = requests.get(f"{BASE}/books", params={"author": "shakespeare", "languages": "en"})
for book in r.json()["results"]:
    print(book["title"])
```

### Using the interactive Swagger UI
1. Open `http://localhost:8000/docs`
2. Click **GET /books** → **Try it out**
3. Enter your filters and click **Execute**
4. The full response with curl command is shown below

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_api.py::test_root_endpoint               PASSED
tests/test_api.py::test_health_check                PASSED
tests/test_api.py::test_list_books_default          PASSED
tests/test_api.py::test_filter_by_gutenberg_ids     PASSED
tests/test_api.py::test_filter_by_languages         PASSED
tests/test_api.py::test_filter_by_mime_type         PASSED
tests/test_api.py::test_filter_by_topic             PASSED
tests/test_api.py::test_filter_by_author            PASSED
tests/test_api.py::test_filter_by_title             PASSED
tests/test_api.py::test_multiple_filters_combined   PASSED
tests/test_api.py::test_pagination                  PASSED

======================== 11 passed ========================
```

---

## Docker

### Run with Docker Compose

```bash
# Create a .env file first (copy from .env.example)
cp .env.example .env

docker compose up --build
```

API will be available at **http://localhost:8000**

### Build image manually

```bash
docker build -t gutenberg-api .
docker run -p 8000:8000 -e DATABASE_URL="postgresql://..." gutenberg-api
```

---

## Deployment (Render)

See [DEPLOY.md](./DEPLOY.md) for full step-by-step instructions.

**Quick summary:**
1. Push to GitHub (`main` branch → production, `develop` branch → staging)
2. Create a PostgreSQL service on Render
3. Restore the dump: `pg_restore --no-owner -d <EXTERNAL_DB_URL> gutendex.dump`
4. Create a Web Service on Render, set `DATABASE_URL` env var
5. Every push auto-deploys; every PR runs CI tests via GitHub Actions

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | — | PostgreSQL connection string |
| `HOST` | No | `0.0.0.0` | Server bind host |
| `PORT` | No | `8000` | Server port |

Copy `.env.example` to `.env` for local development. **Never commit `.env`** — it is gitignored.
