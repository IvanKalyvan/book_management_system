import os
import sys
import json
import csv

from pydantic import ValidationError
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InterfaceError
from fastapi import HTTPException
from datetime import datetime
from io import StringIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from books.models import Book, Genres, Authors
from books.schemas import BookBase, BookSearch, BookUpdate, AuthorBase
from auth.models import User, UserBooks

async def get_books(session: AsyncSession, bookID: int):

    try:
        query = select(Book).where(Book.c.id == bookID)
        result = await session.execute(query)

        book = result.fetchone()

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        book_data = {column: value for column, value in zip(result.keys(), book)}

        if book_data.get('genre') is not None:
            related_query = select(Genres).where(Genres.c.id == book_data['genre'])
            related_result = await session.execute(related_query)
            related_data = related_result.fetchone()

            if related_data is not None:
                book_data['genre'] = related_data.genre_name

        if book_data.get('author') is not None:
            related_query = select(Authors).where(Authors.c.id == book_data['author'])
            related_result = await session.execute(related_query)
            related_data = related_result.fetchone()

            if related_data is not None:
                book_data['author'] = f"{related_data.author_lastName} {related_data.author_firstName}"

        return {"message": "success", "data": book_data}

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

async def create_book(session: AsyncSession, user: User, book_data: BookBase):
    try:

        current_year = datetime.now().year
        if not (1800 <= book_data.published_years <= current_year):
            raise ValueError(f"published_years must be between 1800 and {current_year}")

        genre_name = book_data.genre.strip()
        genre_query = select(Genres.c.id).where(Genres.c.genre_name == genre_name)
        result = await session.execute(genre_query)
        genre_id = result.scalar_one_or_none()

        if genre_id is None:

            raise HTTPException(status_code=400, detail=f"Genre '{genre_name}' not found")

        author_firstName = book_data.author.author_firstName.strip()
        author_lastName = book_data.author.author_lastName.strip()
        author_query = select(Authors.c.id).where(
            Authors.c.author_firstName == author_firstName,
            Authors.c.author_lastName == author_lastName
        )
        result = await session.execute(author_query)
        author_id = result.scalar_one_or_none()

        if author_id is None:
            stmt = insert(Authors).values(
                author_firstName=author_firstName,
                author_lastName=author_lastName
            ).returning(Authors.c.id)
            result = await session.execute(stmt)
            author_id = result.scalar_one()
            await session.commit()

        stmt = insert(Book).values(
            title=book_data.title,
            author=author_id,
            genre=genre_id,
            pages=book_data.pages,
            publisher=book_data.publisher,
            published_years=book_data.published_years,
            language=book_data.language,
            isbn=book_data.isbn
        ).returning(Book.c.id)

        result = await session.execute(stmt)
        book_id = result.scalar_one()
        await session.commit()

        stmt = insert(UserBooks).values(
            user_id=user.id,
            book_id=book_id
        )
        await session.execute(stmt)
        await session.commit()

        return {"message": "Book created successfully", "book_id": book_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {e}")

    except InterfaceError as e:

        await session.rollback()
        raise HTTPException(status_code=422, detail=f"Interface error: {e}")

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

async def search_book(session: AsyncSession, search_data: BookSearch, limit: int = 5, offset: int = 0):
    try:
        author_alias = aliased(Authors)
        genre_alias = aliased(Genres)

        stmt = select(
            Book.c.id,
            Book.c.title,
            Book.c.published_years,
            Book.c.isbn,
            Book.c.pages,
            Book.c.publisher,
            Book.c.language,
            author_alias.c.author_firstName,
            author_alias.c.author_lastName,
            genre_alias.c.genre_name
        ).join(
            author_alias, Book.c.author == author_alias.c.id
        ).join(
            genre_alias, Book.c.genre == genre_alias.c.id
        )

        if search_data.title:
            stmt = stmt.filter(Book.c.title.ilike(f"%{search_data.title}%"))
        if search_data.author_firstName:
            stmt = stmt.filter(author_alias.c.author_firstName.ilike(f"%{search_data.author_firstName}%"))
        if search_data.author_lastName:
            stmt = stmt.filter(author_alias.c.author_lastName.ilike(f"%{search_data.author_lastName}%"))
        if search_data.genre:
            stmt = stmt.filter(genre_alias.c.genre_name.ilike(f"%{search_data.genre}%"))
        if search_data.published_years:
            stmt = stmt.filter(Book.c.published_years == search_data.published_years)
        if search_data.isbn:
            stmt = stmt.filter(Book.c.isbn.ilike(f"%{search_data.isbn}%"))

        stmt = stmt.limit(limit).offset(offset)

        result = await session.execute(stmt)
        books = result.mappings().all()

        return {"books": books, "limit": limit, "offset": offset}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def delete_book_by_id(bookID: int, session: AsyncSession, user: User):

    try:

        book_query = select(Book.c.id).where(Book.c.id == bookID)
        result = await session.execute(book_query)
        book_exists = result.scalar_one_or_none()

        if not book_exists:
            raise HTTPException(status_code=404, detail="Book not found")

        user_book_query = select(UserBooks.c.book_id).where(
            UserBooks.c.book_id == bookID,
            UserBooks.c.user_id == user.id
        )
        result = await session.execute(user_book_query)
        user_has_book = result.scalar_one_or_none()

        if not user_has_book:
            raise HTTPException(status_code=403, detail="You do not own this book")

        delete_user_books = delete(UserBooks).where(
            UserBooks.c.book_id == bookID,
            UserBooks.c.user_id == user.id
        )
        await session.execute(delete_user_books)

        delete_book_stmt = delete(Book).where(Book.c.id == bookID)
        await session.execute(delete_book_stmt)

        await session.commit()
        return {"message": "Book deleted successfully"}

    except HTTPException as e:

        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete book: {e}")

async def update_book_by_id(book_id: int, session: AsyncSession, user: User, book_data: BookUpdate):

    try:

        current_year = datetime.now().year
        if not (1800 <= book_data.published_years <= current_year):
            raise ValueError(f"published_years must be between 1800 and {current_year}")

        stmt = select(Book).where(Book.c.id == book_id)
        result = await session.execute(stmt)
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        user_book_query = select(UserBooks).where(
            UserBooks.c.book_id == book_id,
            UserBooks.c.user_id == user.id
        )
        result = await session.execute(user_book_query)
        user_has_book = result.scalar_one_or_none()

        if not user_has_book:
            raise HTTPException(status_code=403, detail="You do not own this book")

        if 'genre' in book_data.dict(exclude_unset=True):
            genre_name = book_data.genre
            genre_stmt = select(Genres.c.id).where(Genres.c.genre_name == genre_name)
            result = await session.execute(genre_stmt)
            genre = result.scalar_one_or_none()

            if not genre:
                raise HTTPException(status_code=400, detail=f"Genre '{genre_name}' not found")
            else:
                genre_id = genre

            book_data.genre = genre_id

        if 'author' in book_data.dict(exclude_unset=True):
            author_name = book_data.author

            author_stmt = select(Authors.c.id).where(
                Authors.c.author_lastName == author_name.author_lastName,
                Authors.c.author_firstName == author_name.author_firstName
            )
            result = await session.execute(author_stmt)
            author = result.scalar_one_or_none()

            if not author:
                insert_stmt = insert(Authors).values(
                    author_lastName=author_name.author_lastName,
                    author_firstName=author_name.author_firstName,
                ).returning(Authors.c.id)
                result = await session.execute(insert_stmt)
                author_id = result.scalar_one()
            else:
                author_id = author

            book_data.author = author_id

        update_data = {}
        for key, value in book_data.dict(exclude_unset=True).items():
            if key in Book.columns:
                update_data[key] = value
            else:
                raise HTTPException(status_code=400, detail=f"Invalid field {key} for book")

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        stmt = update(Book).where(Book.c.id == book_id).values(update_data)

        await session.execute(stmt)
        await session.commit()
        return {"message": "Book updated successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update book: {e}")

async def process_json(content, session, user):
    try:
        books_data = json.loads(content.decode("utf-8"))

        if isinstance(books_data, dict):
            books_data = [books_data]

        if not isinstance(books_data, list):
            raise HTTPException(status_code=400, detail="Invalid JSON format. Expected a list of books.")

        created_books = []

        for book_data in books_data:

            try:
                book = BookBase(**book_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid book data: {e}")

            book_creation_response = await create_book(session=session, user=user, book_data=book)
            created_books.append(book_creation_response)

        return {"message": f"{len(created_books)} books created successfully"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

async def process_csv(content, session, user):
    try:

        content_str = content.decode("utf-8")

        csv_file = StringIO(content_str)

        reader = csv.DictReader(csv_file)
        books_data = [row for row in reader]

        if not books_data:
            raise HTTPException(status_code=400, detail="CSV is empty or invalid format.")

        created_books = []

        for book_data in books_data:
            try:
                book_base_data = BookBase(
                    title=book_data["Title"],
                    author=AuthorBase(
                        author_firstName=book_data["Author"].split()[0],
                        author_lastName=" ".join(book_data["Author"].split()[1:])
                    ),
                    genre=book_data["Genre"],
                    pages=int(book_data["Pages"]),
                    publisher=book_data["Publisher"],
                    published_years=int(book_data["Year"]),
                    language=book_data["Language"],
                    isbn=book_data["ISBN"]
                )

                book_creation_response = await create_book(session=session, user=user, book_data=book_base_data)
                created_books.append(book_creation_response)

            except ValidationError as e:

                raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

        return {"message": f"{len(created_books)} books created successfully"}

    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV format error: {str(e)}")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
