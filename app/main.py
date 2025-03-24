import os
import sys

from fastapi import FastAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth.routers import auth
from books.routers import books
app = FastAPI(title="Book systerm")

app.include_router(auth)
app.include_router(books)