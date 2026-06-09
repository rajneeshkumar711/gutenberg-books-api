import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint redirects/returns welcome message with links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "openapi" in data


def test_health_check():
    """Verify health check returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_books_default():
    """Verify listing books without parameters returns 25 books sorted by download count descending."""
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    
    assert "count" in data
    assert "next" in data
    assert "previous" in data
    assert "results" in data
    
    results = data["results"]
    assert len(results) <= 25
    
    # Verify decreasing order of popularity (download_count)
    download_counts = [r["download_count"] for r in results if r["download_count"] is not None]
    assert download_counts == sorted(download_counts, reverse=True)
    
    # Check fields in the first book object
    if results:
        book = results[0]
        assert "id" in book
        assert "gutenberg_id" in book
        assert "title" in book
        assert "media_type" in book
        assert "download_count" in book
        assert "authors" in book
        assert "languages" in book
        assert "subjects" in book
        assert "bookshelves" in book
        assert "formats" in book
        
        # Verify structure of nested objects
        for author in book["authors"]:
            assert "name" in author
            assert "birth_year" in author
            assert "death_year" in author
        for fmt in book["formats"]:
            assert "mime_type" in fmt
            assert "url" in fmt


def test_filter_by_gutenberg_ids():
    """Verify filtering by specific Gutenberg IDs."""
    # Let's request Gutenberg IDs 11 and 12
    response = client.get("/books?ids=11,12")
    assert response.status_code == 200
    data = response.json()
    
    results = data["results"]
    # Check that all returned books have Gutenberg ID matching requested ones
    for book in results:
        assert book["gutenberg_id"] in [11, 12]


def test_filter_by_languages():
    """Verify filtering by languages (single and comma-separated)."""
    # Test single language
    response = client.get("/books?languages=en")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        assert "en" in book["languages"]
        
    # Test multiple languages
    response = client.get("/books?languages=fr,de")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        assert any(lang in ["fr", "de"] for lang in book["languages"])


def test_filter_by_mime_type():
    """Verify filtering by format/mime-type."""
    response = client.get("/books?mime_type=text/html")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        # Check if the book contains a format with matching mime_type
        assert any("text/html" in fmt["mime_type"] for fmt in book["formats"])


def test_filter_by_topic():
    """Verify topic filtering matches case-insensitively in subjects or bookshelves."""
    # "child" topic should match bookshelf "Children's Literature" or subject containing "child"
    response = client.get("/books?topic=child")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        match = False
        for subj in book["subjects"]:
            if "child" in subj.lower():
                match = True
                break
        for shelf in book["bookshelves"]:
            if "child" in shelf.lower():
                match = True
                break
        assert match, f"Book {book['title']} did not match 'child' topic in subjects {book['subjects']} or bookshelves {book['bookshelves']}"


def test_filter_by_author():
    """Verify author filtering matches case-insensitively and partially."""
    response = client.get("/books?author=shakespeare")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        assert any("shakespeare" in a["name"].lower() for a in book["authors"])


def test_filter_by_title():
    """Verify title filtering matches case-insensitively and partially."""
    response = client.get("/books?title=romeo")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        assert "romeo" in book["title"].lower()


def test_multiple_filters_combined():
    """Verify combined filtering works correctly."""
    response = client.get("/books?languages=en&topic=drama&author=shakespeare")
    assert response.status_code == 200
    results = response.json()["results"]
    for book in results:
        assert "en" in book["languages"]
        assert any("shakespeare" in a["name"].lower() for a in book["authors"])
        # Check topic (drama) in subjects or bookshelves
        assert any("drama" in s.lower() for s in book["subjects"]) or any("drama" in b.lower() for b in book["bookshelves"])


def test_pagination():
    """Verify next/previous pagination URLs work and count matches."""
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    
    total_count = data["count"]
    if total_count > 25:
        assert data["next"] is not None
        assert data["previous"] is None
        
        # Request next page
        next_url = data["next"]
        # Convert absolute url query string into relative path request
        qs = next_url.split("?")[1]
        response_page2 = client.get(f"/books?{qs}")
        assert response_page2.status_code == 200
        data_page2 = response_page2.json()
        
        assert data_page2["count"] == total_count
        assert len(data_page2["results"]) <= 25
        assert data_page2["previous"] is not None
