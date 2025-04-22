import pytest
from httpx import AsyncClient
from app.models import SwiftCode
from app.schemas import (
    SwiftCodeResponse,
    SwiftCodeWithBranchesResponse,
    CountrySwiftCodesResponse,
    SwiftCodeCreate
)
from app.schemas import SwiftCodeType

@pytest.mark.asyncio
async def test_get_headquarter_swift_code(client: AsyncClient, populated_db):
    """Test retrieving a headquarters SWIFT code with branches"""
    response = await client.get("/api/v1/swift-codes/BOFAUS3NXXX")
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    SwiftCodeWithBranchesResponse.model_validate(data)
    
    assert data["swift_code"] == "BOFAUS3NXXX"
    assert data["code_type"] == SwiftCodeType.HEADQUARTER
    assert len(data["branches"]) >= 1
    assert all(b["code_type"] == SwiftCodeType.BRANCH for b in data["branches"])

@pytest.mark.asyncio
async def test_get_branch_swift_code(client: AsyncClient, populated_db):
    """Test retrieving a branch SWIFT code"""
    response = await client.get("/api/v1/swift-codes/BOFAUS3NBOS")
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    SwiftCodeResponse.model_validate(data)
    
    assert data["swift_code"] == "BOFAUS3NBOS"
    assert data["code_type"] == SwiftCodeType.BRANCH
    assert "branches" not in data

@pytest.mark.asyncio
async def test_get_nonexistent_swift_code(client: AsyncClient, populated_db):
    """Test retrieving a non-existent SWIFT code"""
    response = await client.get("/api/v1/swift-codes/NOTEXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "SWIFT code not found"

@pytest.mark.asyncio
async def test_get_country_swift_codes(client: AsyncClient, populated_db):
    """Test retrieving SWIFT codes by country"""
    response = await client.get("/api/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    CountrySwiftCodesResponse.model_validate(data)
    
    assert data["country_iso2"] == "US"
    assert len(data["swift_codes"]) >= 2
    assert data["count"] == len(data["swift_codes"])

@pytest.mark.asyncio
async def test_get_nonexistent_country_swift_codes(client: AsyncClient, populated_db):
    """Test retrieving codes for non-existent country"""
    response = await client.get("/api/v1/swift-codes/country/XX")
    assert response.status_code == 404
    assert "No SWIFT codes found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_swift_code(client: AsyncClient, db_session):
    """Test creating a new SWIFT code"""
    new_code = SwiftCodeCreate(
        swift_code="TESTGB2LXXX",
        bank_name="TEST BANK",
        address="123 TEST STREET, LONDON",
        country_iso2="GB",
        country_name="UNITED KINGDOM",
        code_type=SwiftCodeType.HEADQUARTER
    )
    
    response = await client.post("/api/v1/swift-codes", json=new_code.model_dump())
    assert response.status_code == 201
    
    # Verify creation
    response = await client.get(f"/api/v1/swift-codes/{new_code.swift_code}")
    assert response.status_code == 200
    created = SwiftCodeResponse.model_validate(response.json())
    assert created.swift_code == new_code.swift_code
    assert created.code_type == SwiftCodeType.HEADQUARTER

@pytest.mark.asyncio
async def test_create_duplicate_swift_code(client: AsyncClient, populated_db):
    """Test creating a duplicate SWIFT code"""
    duplicate_code = SwiftCodeCreate(
        swift_code="BOFAUS3NXXX",
        bank_name="BANK OF AMERICA",
        address="100 NORTH TRYON STREET",
        country_iso2="US",
        country_name="UNITED STATES",
        code_type=SwiftCodeType.HEADQUARTER
    )
    
    response = await client.post("/api/v1/swift-codes", json=duplicate_code.model_dump())
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_swift_code(client: AsyncClient, db_session):
    """Test deleting a SWIFT code"""
    # Create test code
    test_code = SwiftCode(
        swift_code="DELETEMEXXX",
        bank_name="TO DELETE",
        address="123 DELETE ME",
        country_iso2="XX",
        country_name="TEST COUNTRY",
        code_type=SwiftCodeType.HEADQUARTER,
        is_active=True
    )
    db_session.add(test_code)
    await db_session.commit()
    
    # Delete it
    response = await client.delete(f"/api/v1/swift-codes/{test_code.swift_code}")
    assert response.status_code == 200
    assert response.json()["message"] == "SWIFT code deleted successfully"
    
    # Verify deletion
    response = await client.get(f"/api/v1/swift-codes/{test_code.swift_code}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_swift_code(client: AsyncClient, populated_db):
    """Test deleting a non-existent SWIFT code"""
    response = await client.delete("/api/v1/swift-codes/NOTEXIST")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"