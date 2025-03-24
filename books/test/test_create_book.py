# import pytest
# import os
# import sys
# import asyncio
#
# from httpx import AsyncClient
# from fastapi import status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import insert
#
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
#
# from books.models import Book, Authors, Genres
# from auth.test.test_authinticate_user import test_login_success
# from config.test.test_fixture import async_client
# from config.test.test_db_config import test_db
#
#
# @pytest.mark.asyncio
# async def test_create_book_success(async_client: AsyncClient, test_db: AsyncSession, test_login_success):
#
#     genre = insert(Genres).values(id=1, genre_name="Fantasy")
#
#     await test_db.execute(genre)
#     await test_db.commit()
#     await asyncio.sleep(3)
#
#     book_data = {
#         "title": "Test Book",
#         "author": {"author_firstName": "John", "author_lastName": "Doe"},
#         "genre": "Fantasy",
#         "pages": 300,
#         "publisher": "Test Publisher",
#         "published_years": 2021,
#         "language": "English",
#         "isbn": "1234567890"
#     }
#
#     response = await async_client.post("/books/create", json=book_data, cookies={"access_token": test_login_success})
#
#     assert "message" in response.json() == 200
#     assert "message" in response.json()
#     assert response.json()["message"] == "Book created successfully"
#     assert "book_id" in response.json()
#
# # @pytest.mark.asyncio
# # async def test_create_book_invalid_year(async_client: AsyncClient, test_db: AsyncSession, test_login_success):
# #
# #     book_data = {
# #         "title": "Invalid Year Book",
# #         "author": {"author_firstName": "John", "author_lastName": "Doe"},
# #         "genre": "Fantasy",
# #         "pages": 250,
# #         "publisher": "Test Publisher",
# #         "published_years": 1700,
# #         "language": "English",
# #         "isbn": "0987654321"
# #     }
# #
# #     response = await async_client.post("/books/create", json=book_data, cookies={"access_token": test_login_success})
# #
# #     assert response.status_code == status.HTTP_400_BAD_REQUEST
# #     assert "detail" in response.json()
# #     assert response.json()["detail"] == "published_years must be between 1800 and 2025"
#
# # @pytest.mark.asyncio
# # async def test_create_book_invalid_genre(async_client: AsyncClient, test_db: AsyncSession, test_login_success):
# #
# #     book_data = {
# #         "title": "Invalid Genre Book",
# #         "author": {"author_firstName": "John", "author_lastName": "Doe"},
# #         "genre": "Nonexistent Genre",
# #         "pages": 250,
# #         "publisher": "Test Publisher",
# #         "published_years": 2021,
# #         "language": "English",
# #         "isbn": "0987654321"
# #     }
# #
# #     response = await async_client.post("/books/create", json=book_data, cookies={"access_token": test_login_success})
# #
# #     assert response.status_code == 422
# #     assert "detail" in response.json()
# #     assert response.json()["detail"] == "Genre 'Nonexistent Genre' not found"
# #
# # @pytest.mark.asyncio
# # async def test_create_book_missing_data(async_client: AsyncClient, test_db: AsyncSession, test_login_success):
# #
# #     book_data = {
# #         "author": {"author_firstName": "John", "author_lastName": "Doe"},
# #         "genre": "Fantasy",
# #         "published_years": 2021
# #     }
# #
# #     response = await async_client.post("/books/create", json=book_data, cookies={"access_token": test_login_success})
# #
# #     assert response.status_code == 422
# #     assert "detail" in response.json()
# #     assert "field required" in str(response.json()["detail"])
# #
# # @pytest.mark.asyncio
# # async def test_create_book_unauthorized(async_client: AsyncClient, test_db: AsyncSession):
# #
# #     book_data = {
# #         "title": "Unauthorized Book",
# #         "author": {"author_firstName": "John", "author_lastName": "Doe"},
# #         "genre": "Fantasy",
# #         "pages": 300,
# #         "publisher": "Test Publisher",
# #         "published_years": 2021,
# #         "language": "English",
# #         "isbn": "1234567890"
# #     }
# #
# #     response = await async_client.post("/books/create", json=book_data)
# #     assert response.status_code == status.HTTP_401_UNAUTHORIZED
# #     assert "detail" in response.json()
# #     assert response.json()["detail"] == "Token is missing in cookies"
