from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from typing import Annotated
import logging
from fastapi import APIRouter

from .database import init_db, get_db, engine, AsyncSessionLocal
from . import services, utils
from .schemas import SwiftCodeCreate, SwiftCodeResponse, CountrySwiftCodesResponse

# Initialize logging
logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(title="SWIFT Codes API", version="1.0.0")

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

@api_router.get(
    "/v1/swift-codes/{swift_code}",
    response_model=SwiftCodeResponse,
    responses={
        404: {"description": "SWIFT code not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_swift_code(
    swift_code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Retrieve details for a specific SWIFT code.
    """
    try:
        return await services.get_swift_code(db, swift_code)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SWIFT code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.get(
    "/v1/swift-codes/country/{country_code}",
    response_model=CountrySwiftCodesResponse,
    responses={
        404: {"description": "No codes found for country"},
        500: {"description": "Internal server error"}
    }
)
async def get_country_codes(
    country_code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get all SWIFT codes for a specific country.
    """
    try:
        return await services.get_swift_codes_by_country(db, country_code)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching country codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.post(
    "/v1/swift-codes",
    response_model=SwiftCodeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "SWIFT code already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def create_code(
    data: SwiftCodeCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new SWIFT code entry.
    """
    try:
        return await services.create_swift_code(db, data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating SWIFT code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.delete(
    "/v1/swift-codes/{swift_code}",
    responses={
        200: {"description": "SWIFT code deleted successfully"},
        404: {"description": "SWIFT code not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_swift_code(
    swift_code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a SWIFT code entry.
    """
    try:
        deleted = await services.delete_swift_code(db, swift_code)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SWIFT code {swift_code} not found"
            )
        return {"message": "SWIFT code deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting SWIFT code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.get("/health")
async def health_check():
    """Service health check endpoint"""
    return JSONResponse(content={"status": "healthy"})

# Include the router with /api prefix
app.include_router(api_router)

@app.on_event("startup")
async def startup():
    try:
        await init_db()
        async with AsyncSessionLocal() as session:
            await utils.import_swift_codes_from_csv(session)  # No nested transaction
    except Exception as e:
        logging.critical(f"Startup failed: {e}")
        raise