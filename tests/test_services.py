import pytest
from app.services import get_swift_code, create_swift_code
from app.schemas import SwiftCodeCreate
from app.models import SwiftCode
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_swift_code_service(DbSession, PopulatedDb):  # Changed db_session to DbSession
    """Test get_swift_code service function"""
    # Test getting existing SWIFT code
    swift_code = await get_swift_code(DbSession, "BOFAUS3NXXX")
    assert isinstance(swift_code, SwiftCode)
    assert swift_code.swift_code == "BOFAUS3NXXX"
    assert swift_code.bank_name == "BANK OF AMERICA"
    assert swift_code.is_headquarter is True
    
    # Test non-existent SWIFT code
    with pytest.raises(HTTPException) as exc_info:
        await get_swift_code(DbSession, "NONEXISTENT")
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_create_swift_code_service(DbSession):  # Changed db_session to DbSession
    """Test create_swift_code service function"""
    new_code = SwiftCodeCreate(
        swiftCode="TESTGB2LXXX",  
        bankName="TEST BANK",
        address="123 TEST STREET",
        countryISO2="GB",
        countryName="UNITED KINGDOM",
        isHeadquarter=True
    )
    
    # Test successful creation
    result = await create_swift_code(DbSession, new_code)
    assert result.swift_code == "TESTGB2LXXX"
    assert result.bank_name == "TEST BANK"
    assert result.is_active is True
    
    # Test duplicate creation
    with pytest.raises(HTTPException) as exc_info:
        await create_swift_code(DbSession, new_code)
    assert exc_info.value.status_code == 400