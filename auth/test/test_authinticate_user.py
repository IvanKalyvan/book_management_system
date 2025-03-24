import sys
import os
import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config.test.test_db_config import test_db
from config.test.test_fixture import async_client
from auth.schemas import UserCreate
from auth.models import User
from auth.utils import register_user

user_data = {
    "email": "testuser@example.com",
    "password": "password123",
    "confirmPassword": "password123"
}

@pytest.fixture
async def test_login_success(async_client: AsyncClient, test_db: AsyncSession):

    user_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "confirmPassword": "password123"
    }

    user_create = UserCreate(**user_data)
    await register_user(test_db, user_create)

    result = await test_db.execute(select(User).filter_by(email="testuser@example.com"))
    user = result.scalars().first()
    assert user is not None

    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }

    response = await async_client.post("auth/login", json=login_data)

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.cookies.get("access_token") is not None
    assert response.cookies["access_token"] is not None

    return response.cookies["access_token"]

@pytest.mark.asyncio
async def test_register_user_password_mismatch(async_client: AsyncClient, test_db: AsyncSession):

    user_data_invalid = user_data.copy()
    user_data_invalid["confirmPassword"] = "wrongpassword"

    response = await async_client.post("auth/register", json=user_data_invalid)

    assert response.status_code == 400
    assert response.json().get("detail") == "Passwords do not match"


@pytest.mark.asyncio
async def test_register_user_invalid_password(async_client: AsyncClient, test_db: AsyncSession):

    user_data_invalid = user_data.copy()
    user_data_invalid["password"] = "short"
    user_data_invalid["confirmPassword"] = "short"

    response = await async_client.post("auth/register", json=user_data_invalid)

    assert response.status_code == 400
    assert response.json().get("detail") == "Password must be at least 8 characters long and contain no special characters."
