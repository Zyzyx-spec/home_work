from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SwiftCodeBase(BaseModel):
    swift_code: str = Field(..., min_length=8, max_length=11, alias="swiftCode")
    bank_name: str = Field(..., min_length=2, max_length=255, alias="bankName")
    address: str = Field(..., min_length=5, max_length=512)
    country_iso2: str = Field(..., min_length=2, max_length=2, alias="countryISO2")
    country_name: str = Field(..., alias="countryName")
    is_headquarter: bool = Field(..., alias="isHeadquarter")
    time_zone: Optional[str] = Field(None, alias="timeZone")

    class Config:
        allow_population_by_field_name = True

class SwiftCodeResponse(SwiftCodeBase):
    id: str
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

class BranchResponse(BaseModel):
    swiftCode: str
    bankName: str
    address: str
    countryISO2: str
    isHeadquarter: bool

class SwiftCodeWithBranchesResponse(SwiftCodeResponse):
    branches: List[BranchResponse] = []

class CountrySwiftCodesResponse(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[BranchResponse]

class SwiftCodeCreate(SwiftCodeBase):
    pass