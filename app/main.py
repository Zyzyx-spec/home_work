from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Union
from contextlib import asynccontextmanager
import logging
from .database import get_db, init_db
from . import services
from .schemas import (
    SwiftCodeBasic,
    SwiftCodeWithBranches,
    CountrySwiftCodesResponse,
    SwiftCodeCreate,
    SwiftCodeCreateResponse,
    SwiftCodeDeleteResponse
)

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Zarządzanie cyklem życia aplikacji"""
    await init_db()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")

# Inicjalizacja aplikacji
app = FastAPI(
    title="SWIFT Codes API",
    version="1.0.0",
    lifespan=lifespan
)

# Router dla endpointów API
api_router = APIRouter(prefix="/api")

@api_router.get(
    "/v1/swift-codes/{swift_code}",
    response_model=Union[SwiftCodeWithBranches, SwiftCodeBasic],
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
    Pobierz szczegóły kodu SWIFT (headquarters lub branch)
    - Dla headquarters zwraca również listę branches
    - Dla branch zwraca tylko podstawowe informacje
    """
    return await services.get_swift_code(db, swift_code)

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
    Pobierz wszystkie kody SWIFT dla określonego kraju
    - Zwraca zarówno headquarters jak i branches
    - Sortowane alfabetycznie po kodzie SWIFT
    """
    return await services.get_swift_codes_by_country(db, country_code)

@api_router.post(
    "/v1/swift-codes",
    response_model=SwiftCodeCreateResponse,
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
    Utwórz nowy wpis kodu SWIFT
    - Wymaga wszystkich pól zgodnie ze schematem
    - Automatycznie konwertuje kody kraju na wielkie litery
    """
    return await services.create_swift_code(db, data)

@api_router.delete(
    "/v1/swift-codes/{swift_code}",
    response_model=SwiftCodeDeleteResponse,
    responses={
        404: {"description": "SWIFT code not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_swift_code(
    swift_code: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Usuń kod SWIFT (soft delete)
    - W rzeczywistości ustawia flagę is_active na False
    - Nie usuwa fizycznie rekordu z bazy danych
    """
    return await services.delete_swift_code(db, swift_code)

@api_router.get("/health", tags=["Health"])
async def health_check():
    """Endpoint sprawdzający stan aplikacji"""
    return JSONResponse(content={"status": "healthy"})

# Dołącz router do aplikacji
app.include_router(api_router)