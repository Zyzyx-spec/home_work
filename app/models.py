from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from .database import Base

class SwiftCode(Base):
    __tablename__ = "swift_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_iso2 = Column(String(2), nullable=False, index=True)
    swift_code = Column(String(11), nullable=False, unique=True, index=True)
    code_type = Column(String(20), nullable=False)
    bank_name = Column(String(255), nullable=False)
    address = Column(String(512), nullable=False)
    town_name = Column(String(100))
    country_name = Column(String(100), nullable=False)
    time_zone = Column(String(50))
    is_headquarter = Column(Boolean, nullable=False, default=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        Index('ix_swift_branches', 'swift_code', 'is_headquarter'),
    )