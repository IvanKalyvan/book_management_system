import pytest
import os
import sys

from httpx import AsyncClient, ASGITransport

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.main import app

@pytest.fixture
async def async_client():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:

        yield client