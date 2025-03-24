import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import Table, Column, BigInteger, String, ForeignKey, Integer
from config.db_config import metaData

Book = Table(
    "Book",
    metaData,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False, index=True),
    Column("author", ForeignKey("Authors.id"), nullable=False, index=True),
    Column("pages", Integer, nullable=False, index=True),
    Column("genre", ForeignKey("Genres.id"), nullable=False, index=True),
    Column("publisher", String, nullable=False, index=True),
    Column("published_years", Integer, nullable=False, index=True),
    Column("language", String, nullable=False, index=True),
    Column("isbn", String, nullable=False, index=True),
)

Genres = Table(
    "Genres",
    metaData,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("genre_name", String, nullable=False),
)

Authors = Table(
    "Authors",
    metaData,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("author_lastName", String, nullable=False),
    Column("author_firstName", String, nullable=False)
)