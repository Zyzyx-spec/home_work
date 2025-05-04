import pytest
from httpx import AsyncClient
from app.models import SwiftCode

@pytest.mark.asyncio
async def test_get_swift_code(Client: AsyncClient, PopulatedDb):  # Changed client to Client and populated_db to PopulatedDb
    """Test GET /swift-codes/{swift_code} endpoint"""
    response = await Client.get("/api/v1/swift-codes/BOFAUS3NXXX")
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "BOFAUS3NXXX"
    assert data["isHeadquarter"] is True

async def test_create_swift_code(Client: AsyncClient):
    new_code = {
        "swift_code": "TESTGB2LXXX",  # snake_case
        "bank_name": "TEST BANK",
        "address": "123 TEST STREET, LONDON",
        "country_iso2": "GB",
        "country_name": "UNITED KINGDOM",
        "is_headquarter": True
    }
    response = await Client.post("/api/v1/swift-codes", json=new_code)
    assert response.status_code == 201