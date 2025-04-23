import pytest
from httpx import AsyncClient
from app.models import SwiftCode

@pytest.mark.asyncio
async def test_get_swift_code(Client: AsyncClient, PopulatedDb):  # Changed client to Client and populated_db to PopulatedDb
    """Test GET /swift-codes/{swift_code} endpoint"""
    response = await Client.get("/swift-codes/BOFAUS3NXXX")
    assert response.status_code == 200
    data = response.json()
    assert data["swift_code"] == "BOFAUS3NXXX"
    assert data["is_headquarter"] is True

@pytest.mark.asyncio
async def test_create_swift_code(Client: AsyncClient):
    """Test POST /swift-codes endpoint"""
    new_code = {
        "swiftCode": "TESTGB2LXXX",
        "bankName": "TEST BANK",
        "address": "123 TEST STREET, LONDON",
        "countryISO2": "GB",
        "countryName": "UNITED KINGDOM",
        "isHeadquarter": True
    }
    response = await Client.post("/swift-codes/", json=new_code)  # Note trailing slash
    assert response.status_code == 201