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
async def test_create_swift_code(client: AsyncClient):
    """Test POST /swift-codes endpoint"""
    new_code = {
        "swiftCode": "TESTGB2LXXX",  
        "bankName": "TEST BANK",
        "address": "123 TEST STREET, LONDON",
        "countryISO2": "GB",
        "countryName": "UNITED KINGDOM",
        "isHeadquarter": True
    }
    response = await client.post("/swift-codes", json=new_code)
    assert response.status_code == 201
    assert response.json()["swift_code"] == "TESTGB2LXXX"