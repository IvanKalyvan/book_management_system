import pytest
import os
import sys

from sqlalchemy import insert

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from books.models import Book, Authors, Genres

@pytest.mark.asyncio
async def test_get_book_by_id_success(async_client, session):

    book_data = {
        "title": "Test Book",
        "author": {"author_firstName": "John", "author_lastName": "Doe"},
        "genre": "Fantasy",
        "pages": 300,
        "publisher": "Test Publisher",
        "published_years": 2021,
        "language": "English",
        "isbn": "1234567890"
    }

    await async_client.post("/books/create", json=book_data)

    response = await async_client.get("/books/bookID=1")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "success"
    assert data["data"]["title"] == "Test Book"
    assert "genre" in data["data"]
    assert "author" in data["data"]


@pytest.mark.asyncio
async def test_get_book_by_id_not_found(async_client, session):

    response = await async_client.get("/books/bookID=999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"
