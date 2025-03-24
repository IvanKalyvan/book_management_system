import os
import sys
import jwt

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.db_config import get_session
from config.app_config import jwt_secret, jwt_algorithm
from auth.models import User

async def get_current_user(request: Request, session: AsyncSession = Depends(get_session)):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token is missing in cookies")

    try:

        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        query = select(User).where(User.c.email == email)
        user = await session.execute(query)
        user = user.fetchone()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
