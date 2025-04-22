import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services import (
    get_swift_code,
    get_swift_codes_by_country,
    create_swift_code,
    delete_swift_code,
    update_swift_code,
    deactivate_swift_code
)
from app.models import SwiftCode
from app.schemas import (
    SwiftCodeCreate,
    SwiftCodeUpdate,
    SwiftCodeResponse,
    SwiftCodeWithBranchesResponse,
    CountrySwiftCodesResponse,
    SwiftCodeType
)

@pytest.mark.asyncio
async def test_get_swift_code_headquarter(db_session: AsyncSession, populated_db):
    """Test retrieving headquarters with branches"""
    result = await get_swift_code(db_session, "BOFAUS3NXXX")
    
    assert isinstance(result, SwiftCodeWithBranchesResponse)
    assert result.swift_code == "BOFAUS3NXXX"
    assert result.code_type == SwiftCodeType.HEADQUARTER
    assert len(result.branches) >= 1
    assert all(b.code_type == SwiftCodeType.BRANCH for b in result.branches)

@pytest.mark.asyncio
async def test_get_swift_code_branch(db_session: AsyncSession, populated_db):
    """Test retrieving branch details"""
    result = await get_swift_code(db_session, "BOFAUS3NBOS")
    
    assert isinstance(result, SwiftCodeResponse)
    assert result.swift_code == "BOFAUS3NBOS"
    assert result.code_type == SwiftCodeType.BRANCH
    assert not hasattr(result, "branches")

@pytest.mark.asyncio
async def test_get_nonexistent_swift_code(db_session: AsyncSession):
    """Test retrieving non-existent code"""
    with pytest.raises(HTTPException) as exc_info:
        await get_swift_code(db_session, "NOTEXIST")
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_get_country_swift_codes(db_session: AsyncSession, populated_db):
    """Test retrieving codes by country"""
    result = await get_swift_codes_by_country(db_session, "US")
    
    assert isinstance(result, CountrySwiftCodesResponse)
    assert result.country_iso2 == "US"
    assert len(result.swift_codes) >= 2
    assert result.count == len(result.swift_codes)

@pytest.mark.asyncio
async def test_get_nonexistent_country_swift_codes(db_session: AsyncSession):
    """Test retrieving codes for non-existent country"""
    with pytest.raises(HTTPException) as exc_info:
        await get_swift_codes_by_country(db_session, "XX")
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_create_swift_code(db_session: AsyncSession):
    """Test creating new SWIFT code"""
    new_code = SwiftCodeCreate(
        swift_code="TESTGB2LXXX",
        bank_name="TEST BANK",
        address="123 TEST STREET, LONDON",
        country_iso2="GB",
        country_name="UNITED KINGDOM",
        code_type=SwiftCodeType.HEADQUARTER
    )
    
    result = await create_swift_code(db_session, new_code)
    assert isinstance(result, SwiftCodeResponse)
    assert result.swift_code == new_code.swift_code
    
    # Verify creation
    verify = await get_swift_code(db_session, new_code.swift_code)
    assert verify.swift_code == new_code.swift_code

@pytest.mark.asyncio
async def test_create_duplicate_swift_code(db_session: AsyncSession, populated_db):
    """Test creating duplicate code"""
    duplicate_code = SwiftCodeCreate(
        swift_code="BOFAUS3NXXX",
        bank_name="BANK OF AMERICA",
        address="100 NORTH TRYON STREET",
        country_iso2="US",
        country_name="UNITED STATES",
        code_type=SwiftCodeType.HEADQUARTER
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await create_swift_code(db_session, duplicate_code)
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_update_swift_code(db_session: AsyncSession, populated_db):
    """Test updating SWIFT code details"""
    update_data = SwiftCodeUpdate(
        bank_name="NEW BANK NAME",
        address="UPDATED ADDRESS"
    )
    
    result = await update_swift_code(db_session, "BOFAUS3NBOS", update_data)
    assert isinstance(result, SwiftCodeResponse)
    assert result.bank_name == "NEW BANK NAME"
    assert result.address == "UPDATED ADDRESS"

@pytest.mark.asyncio
async def test_deactivate_swift_code(db_session: AsyncSession, populated_db):
    """Test deactivating a SWIFT code"""
    result = await deactivate_swift_code(db_session, "BOFAUS3NBOS")
    assert isinstance(result, SwiftCodeResponse)
    assert result.is_active is False

@pytest.mark.asyncio
async def test_delete_swift_code(db_session: AsyncSession):
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
    deleted = await delete_swift_code(db_session, "DELETEMEXXX")
    assert deleted is True
    
    # Verify deletion
    with pytest.raises(HTTPException) as exc_info:
        await get_swift_code(db_session, "DELETEMEXXX")
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_swift_code(db_session: AsyncSession):
    """Test deleting non-existent code"""
    deleted = await delete_swift_code(db_session, "NOTEXIST")
    assert deleted is False