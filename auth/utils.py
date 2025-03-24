import os
import sys

import bcrypt
import jwt
import re

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Response
from sqlalchemy import insert, select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.app_config import jwt_secret, jwt_algorithm
from auth.schemas import UserCreate
from auth.models import User

def verify_password(plain_password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)
    return encoded_jwt


def validate_password(password: str) -> bool:

    if len(password) < 8 or re.search(r'[^a-zA-Z0-9]', password):
        return False
    return True


async def register_user(session: AsyncSession, user: UserCreate):

    if user.password != user.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    if not validate_password(user.password):

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password must be at least 8 characters long and contain no special characters.")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = insert(User).values(email=user.email, password=hashed_password)
    await session.execute(new_user)
    await session.commit()

    return {"message": "User registered successfully"}


async def authenticate_user(session: AsyncSession, email: str, password: str, response: Response):

    query = select(User).where(User.c.email == email)
    result = await session.execute(query)
    user = result.fetchone()

    if user is None or not verify_password(password, user.password):

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
    )

    return {"message": "Successfully logged in"}