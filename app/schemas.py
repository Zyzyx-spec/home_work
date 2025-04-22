from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SwiftCodeBase(BaseModel):
    swiftCode: str = Field(..., min_length=8, max_length=11)
    bankName: str = Field(..., min_length=2, max_length=255)
    address: str = Field(..., min_length=5, max_length=512)
    countryISO2: str = Field(..., min_length=2, max_length=2)
    countryName: str
    isHeadquarter: bool
    timeZone: Optional[str] = None

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