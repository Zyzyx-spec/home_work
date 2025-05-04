from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .database import AsyncSession
from .models import SwiftCode
from .schemas import SwiftCodeBasic, SwiftCodeWithBranches, CountrySwiftCodesResponse, SwiftCodeCreate

async def get_swift_code(db: AsyncSession, swift_code: str):
    try:
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

        base_data = SwiftCodeBasic(
            swiftCode=main_record.swift_code,
            bankName=main_record.bank_name,
            address=main_record.address,
            countryISO2=main_record.country_iso2,
            isHeadquarter=main_record.is_headquarter
        )

        if main_record.is_headquarter:
            branches_result = await db.execute(
                select(SwiftCode)
                .where(SwiftCode.swift_code.like(f"{main_record.swift_code[:8]}%"))
                .where(SwiftCode.swift_code != main_record.swift_code)
                .where(SwiftCode.is_headquarter == False)
                .where(SwiftCode.is_active == True)
            )
            branches = [
                SwiftCodeBasic(
                    swiftCode=b.swift_code,
                    bankName=b.bank_name,
                    address=b.address,
                    countryISO2=b.country_iso2,
                    isHeadquarter=b.is_headquarter
                ) for b in branches_result.scalars().all()
            ]
            return SwiftCodeWithBranches(
                **base_data.model_dump(),
                countryName=main_record.country_name,
                branches=branches
            )
        else:
            return SwiftCodeWithBranches(
                **base_data.model_dump(),
                countryName=main_record.country_name
            )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

async def get_swift_codes_by_country(db: AsyncSession, country_code: str):
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
            swiftCodes=[
                SwiftCodeBasic(
                    swiftCode=c.swift_code,
                    bankName=c.bank_name,
                    address=c.address,
                    countryISO2=c.country_iso2,
                    isHeadquarter=c.is_headquarter
                ) for c in codes
            ]
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

async def create_swift_code(db: AsyncSession, data: SwiftCodeCreate):
    try:
        existing = await db.execute(
            select(SwiftCode.swift_code)
            .where(SwiftCode.swift_code == data.swiftCode.upper())
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SWIFT code {data.swiftCode} already exists"
            )

        new_code = SwiftCode(
            swift_code=data.swiftCode.upper(),
            bank_name=data.bankName,
            address=data.address,
            country_iso2=data.countryISO2.upper(),
            country_name=data.countryName.upper(),
            is_headquarter=data.isHeadquarter,
            code_type='headquarter' if data.isHeadquarter else 'branch',
            is_active=True
        )

        db.add(new_code)
        await db.commit()
        return {"message": "SWIFT code created successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SWIFT code"
        )

async def delete_swift_code(db: AsyncSession, swift_code: str):
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
        return {"message": "SWIFT code deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete SWIFT code"
        )