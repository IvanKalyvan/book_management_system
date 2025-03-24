import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import Table, Column, String, ForeignKey, BigInteger, TIMESTAMP, func
from config.db_config import metaData

User = Table(

    "User",
    metaData,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("email", String, nullable=False),
    Column("password", String, nullable=False),
    Column("createAt", TIMESTAMP, nullable=False, default=func.now()),

)

UserBooks = Table(
    "UserBooksMerge",
    metaData,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("User.id")),
    Column("book_id", BigInteger, ForeignKey("Book.id"))
)