import pytest
from app.services import get_swift_code, create_swift_code
from app.schemas import SwiftCodeCreate
from app.models import SwiftCode

@pytest.mark.asyncio
async def test_get_swift_code_service(db_session, populated_db):
    """Test get_swift_code service function"""
    swift_code = await get_swift_code(db_session, "BOFAUS3NXXX")
    assert isinstance(swift_code, SwiftCode)
    assert swift_code.swift_code == "BOFAUS3NXXX"
    assert swift_code.is_headquarter is True

@pytest.mark.asyncio
async def test_create_swift_code_service(db_session):
    """Test create_swift_code service function"""
    new_code = SwiftCodeCreate(
        swift_code="TESTGB2LXXX",
        bank_name="TEST BANK",
        address="123 TEST STREET",
        country_iso2="GB",
        country_name="UNITED KINGDOM",
        is_headquarter=True
    )
    result = await create_swift_code(db_session, new_code)
    assert result.swift_code == "TESTGB2LXXX"
    assert result.bank_name == "TEST BANK"