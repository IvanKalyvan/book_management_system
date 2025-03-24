import sys
import os
import pytest

from httpx import AsyncClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, session):

    register_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "confirmPassword": "password123"
    }

    response = await async_client.post("/auth/register", json=register_data)

    assert response.status_code == 200

    register_data = {
        "email": "testuser@example.com",
        "password": "password123",
    }

    response = await async_client.post("/auth/login", json=register_data)

    assert response.status_code == 200
    token = async_client.cookies.get("access_token")
    assert token is not None

@pytest.mark.asyncio
async def test_register_user_password_mismatch(async_client: AsyncClient, session):

    register_data = {
        "email": "testuser@example.com",
        "password": "password123",
    }

    user_data = register_data.copy()
    user_data["confirmPassword"] = "wrongpassword"

    response = await async_client.post("auth/register", json=user_data)

    assert response.status_code == 400
    assert response.json().get("detail") == "Passwords do not match"


@pytest.mark.asyncio
async def test_register_user_invalid_password(async_client: AsyncClient, session):

    user_data = {

        "email": "testuser@example.com",
        "password": "short",
        "confirmPassword": "short"
    }

    response = await async_client.post("auth/register", json=user_data)

    assert response.status_code == 400
    assert response.json().get("detail") == "Password must be at least 8 characters long and contain no special characters."
