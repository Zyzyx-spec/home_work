from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, Union

class SwiftCodeBasic(BaseModel):
    swiftCode: str = Field(..., min_length=8, max_length=11)
    bankName: str = Field(..., min_length=2, max_length=255)
    address: str = Field(..., min_length=5, max_length=512)
    countryISO2: str = Field(..., min_length=2, max_length=2)
    isHeadquarter: bool

    model_config = ConfigDict(populate_by_name=True)

class SwiftCodeWithBranches(SwiftCodeBasic):
    countryName: str
    branches: List[SwiftCodeBasic] = []

class CountrySwiftCodesResponse(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeBasic]

    model_config = ConfigDict(populate_by_name=True)

class SwiftCodeCreate(BaseModel):
    swiftCode: str = Field(..., min_length=8, max_length=11)
    bankName: str = Field(..., min_length=2, max_length=255)
    address: str = Field(..., min_length=5, max_length=512)
    countryISO2: str = Field(..., min_length=2, max_length=2)
    countryName: str
    isHeadquarter: bool

    model_config = ConfigDict(populate_by_name=True)

class SwiftCodeCreateResponse(BaseModel):
    message: str

class SwiftCodeDeleteResponse(BaseModel):
    message: str