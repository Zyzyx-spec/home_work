import pytest
from httpx import AsyncClient
from app.models import SwiftCode

@pytest.mark.asyncio
async def test_get_swift_code(client: AsyncClient, populated_db):
    """Test GET /swift-codes/{swift_code} endpoint"""
    response = await client.get("/swift-codes/BOFAUS3NXXX")
    assert response.status_code == 200
    data = response.json()
    assert data["swift_code"] == "BOFAUS3NXXX"
    assert data["is_headquarter"] is True

@pytest.mark.asyncio
async def test_create_swift_code(client: AsyncClient, db_session):
    """Test POST /swift-codes endpoint"""
    new_code = {
        "swift_code": "TESTGB2LXXX",
        "bank_name": "TEST BANK",
        "address": "123 TEST STREET, LONDON",
        "country_iso2": "GB",
        "country_name": "UNITED KINGDOM",
        "is_headquarter": True,
        "is_active": True
    }
    response = await client.post("/swift-codes", json=new_code)
    assert response.status_code == 201
    assert response.json()["swift_code"] == "TESTGB2LXXX"