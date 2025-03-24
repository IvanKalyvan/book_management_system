import os
import sys

from fastapi import Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth.schemas import UserCreate, UserLogin
from config.db_config import get_session
from auth.utils import register_user, authenticate_user

auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth.post("/register")
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):

    return await register_user(session, user)

@auth.post("/login")
async def login(user: UserLogin, response: Response, session: AsyncSession = Depends(get_session)):

    return await authenticate_user(session, user.email, user.password, response)