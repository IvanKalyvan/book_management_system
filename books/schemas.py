from pydantic import BaseModel
from typing import Optional
from fastapi import Query

class AuthorBase(BaseModel):

    author_firstName: str
    author_lastName: str

    class Config:
        orm_mode = True

class AuthorBaseUpdate(BaseModel):

    author_firstName: Optional[str] = None
    author_lastName: Optional[str] = None
    class Config:
        orm_mode = True

class BookBase(BaseModel):

    title: str
    author: AuthorBase
    genre: str
    pages: int
    publisher: str
    published_years: int
    language: str
    isbn: str

    class Config:
        orm_mode = True

class BookSearch(BaseModel):

    title: Optional[str] = Query(None)
    author_firstName: Optional[str] = Query(None)
    author_lastName: Optional[str] = Query(None)
    genre: Optional[str] = Query(None)
    published_years: Optional[int] = Query(None)
    isbn: Optional[str] = Query(None)

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):

    title: Optional[str] = None
    author: Optional[AuthorBaseUpdate] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None
    published_years: Optional[int] = None
    language: Optional[str] = None
    isbn: Optional[str] = None

    class Config:
        orm_mode = True