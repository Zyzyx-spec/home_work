from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import logging
from .database import AsyncSession
from .models import SwiftCode
from .schemas import SwiftCodeResponse, SwiftCodeWithBranchesResponse, CountrySwiftCodesResponse, SwiftCodeCreate

logger = logging.getLogger(__name__)

async def get_swift_code(db: AsyncSession, swift_code: str):
    """Retrieve SWIFT code with branches if headquarters"""
    try:
        # Get main record
        result = await db.execute(
            select(SwiftCode)
            .where(SwiftCode.swift_code == swift_code.upper())
            .where(SwiftCode.is_active == True)
        )
        main_record = result.scalars().first()

        if not main_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )

        # Convert to response model
        response_data = {
            "id": str(main_record.id),
            "swiftCode": main_record.swift_code,
            "bankName": main_record.bank_name,
            "address": main_record.address,
            "countryISO2": main_record.country_iso2,
            "countryName": main_record.country_name,
            "isHeadquarter": main_record.is_headquarter,
            "timeZone": main_record.time_zone,
            "isActive": main_record.is_active,
            "createdAt": main_record.created_at,
            "updatedAt": main_record.updated_at
        }

        # If headquarters, get branches
        if main_record.is_headquarter:
            branches_result = await db.execute(
                select(SwiftCode)
                .where(SwiftCode.swift_code.like(f"{main_record.swift_code[:8]}%"))
                .where(SwiftCode.swift_code != main_record.swift_code)
                .where(SwiftCode.is_headquarter == False)
                .where(SwiftCode.is_active == True)
            )
            branches = branches_result.scalars().all()
            
            return SwiftCodeWithBranchesResponse(
                **response_data,
                branches=[{
                    "swiftCode": b.swift_code,
                    "bankName": b.bank_name,
                    "address": b.address,
                    "countryISO2": b.country_iso2,
                    "isHeadquarter": b.is_headquarter
                } for b in branches]
            )
        
        return SwiftCodeResponse(**response_data)

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

async def get_swift_codes_by_country(db: AsyncSession, country_code: str):
    """Get all SWIFT codes for a country"""
    try:
        result = await db.execute(
            select(SwiftCode)
            .where(SwiftCode.country_iso2 == country_code.upper())
            .where(SwiftCode.is_active == True)
            .order_by(SwiftCode.swift_code)
        )
        codes = result.scalars().all()

        if not codes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SWIFT codes found for country {country_code}"
            )

        return CountrySwiftCodesResponse(
            countryISO2=country_code.upper(),
            countryName=codes[0].country_name,
            swiftCodes=[{
                "swiftCode": c.swift_code,
                "bankName": c.bank_name,
                "address": c.address,
                "countryISO2": c.country_iso2,
                "isHeadquarter": c.is_headquarter
            } for c in codes]
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

async def create_swift_code(db: AsyncSession, data: SwiftCodeCreate):
    """Create new SWIFT code"""
    try:
        # Check if code exists
        existing = await db.execute(
            select(SwiftCode.swift_code)
            .where(SwiftCode.swift_code == data.swift_code.upper())
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SWIFT code {data.swift_code} already exists"
            )

        new_code = SwiftCode(
            swift_code=data.swift_code.upper(),
            bank_name=data.bankName,
            address=data.address,
            country_iso2=data.countryISO2.upper(),
            country_name=data.countryName.upper(),
            is_headquarter=data.isHeadquarter,
            time_zone=data.timeZone if hasattr(data, 'timeZone') else None,
            code_type='headquarter' if data.isHeadquarter else 'branch'
        )

        db.add(new_code)
        await db.commit()
        await db.refresh(new_code)

        return {"message": "SWIFT code created successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SWIFT code"
        )

async def delete_swift_code(db: AsyncSession, swift_code: str):
    """Soft delete SWIFT code"""
    try:
        result = await db.execute(
            select(SwiftCode)
            .where(SwiftCode.swift_code == swift_code.upper())
        )
        record = result.scalars().first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )

        record.is_active = False
        await db.commit()

        return {"message": "SWIFT code deactivated successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate SWIFT code"
        )