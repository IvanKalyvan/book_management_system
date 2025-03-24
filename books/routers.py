import os
import sys

from fastapi import Depends, APIRouter, Query, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.db_config import get_session
from books.utils import (get_books, create_book, search_book, delete_book_by_id, update_book_by_id,
                         process_csv, process_json)
from app.utils import get_current_user
from auth.models import User
from books.schemas import BookBase, BookSearch, BookUpdate

books = APIRouter(
    prefix="/books",
    tags=["books"]
)

@books.get("/bookID={bookID}")
async def get_book_by_id(bookID: int, session: AsyncSession = Depends(get_session)):

    return await get_books(session, bookID)

@books.post("/create")
async def create_book_record(book_data: BookBase, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):

    return await create_book(session, user, book_data)

@books.get("/search")
async def get_books_with_params(
    search_data: BookSearch = Depends(),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return await search_book(session, search_data, limit, offset)

@books.delete("/delete={bookID}")
async def delete_book(bookID: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):

    return await delete_book_by_id(bookID, session, user)

@books.put("/books/{book_id}")
async def put_book(book_id: int,
                   book_data: BookUpdate,
                   session: AsyncSession = Depends(get_session),
                   user: User = Depends(get_current_user)):
    return await update_book_by_id(book_id, session, user, book_data)

@books.patch("/books/{book_id}")
async def patch_book(book_id: int,
                     book_data: BookUpdate,
                     session: AsyncSession = Depends(get_session),
                     user: User = Depends(get_current_user)):
    return await update_book_by_id(book_id, session, user, book_data)

@books.post("/bulk-import-books")
async def bulk_import_books(file: UploadFile = File(...), session: AsyncSession = Depends(get_session), user = Depends(get_current_user)):

    try:

        file_content = await file.read()

        if file.filename.endswith(".csv"):

            await process_csv(file_content, session, user)

        elif file.filename.endswith(".json"):

            await process_json(file_content, session, user)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only CSV and JSON are allowed.")

        #await bulk_insert_books(books["created_books"])

        return {"message": "Books successfully imported"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing books: {str(e)}")