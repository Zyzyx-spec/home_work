import csv
import logging
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from .models import SwiftCode

logger = logging.getLogger(__name__)

async def import_swift_codes_from_csv(db: AsyncSession, filepath: str = "/app/Interns_2025_SWIFT_CODES.csv") -> Dict[str, int]:
    """
    Import SWIFT codes from CSV file into database with proper transaction handling.
    
    Args:
        db: Async SQLAlchemy session
        filepath: Path to CSV file
        
    Returns:
        Dictionary with import statistics:
        {
            "imported": number of successfully imported records,
            "total": total rows processed, 
            "skipped": number of failed rows
        }
        
    Raises:
        HTTPException: For file errors or validation failures
    """
    logger.info(f"Starting CSV import from {filepath}")

    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as csvfile:
            # Read and filter non-empty lines
            lines = [line for line in csvfile if line.strip()]
            if not lines:
                raise HTTPException(status_code=400, detail="CSV file is empty")
                
            reader = csv.DictReader(lines)
            
            # Validate required columns
            required_columns = {
                'COUNTRY ISO2 CODE',
                'SWIFT CODE', 
                'CODE TYPE',
                'NAME',
                'ADDRESS',
                'TOWN NAME',
                'COUNTRY NAME',
                'TIME ZONE'
            }
            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required columns: {missing_columns}"
                )

            imported = 0
            batch = []
            batch_size = 100  # Optimal batch size for performance
            
            async with db.begin():  # Main transaction
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Create record from CSV row
                        record = SwiftCode(
                            country_iso2=row['COUNTRY ISO2 CODE'].strip().upper(),
                            swift_code=row['SWIFT CODE'].strip().upper(),
                            code_type=row['CODE TYPE'].strip().lower(),
                            bank_name=row['NAME'].strip(),
                            address=f"{row['ADDRESS']}, {row['TOWN NAME']}",
                            town_name=row['TOWN NAME'].strip(),
                            country_name=row['COUNTRY NAME'].strip(),
                            time_zone=row['TIME ZONE'].strip() if row['TIME ZONE'] else None,
                            is_headquarter=row['CODE TYPE'].strip().upper() == 'HEADQUARTER',
                            is_active=True
                        )
                        batch.append(record)
                        
                        # Process batch when full
                        if len(batch) >= batch_size:
                            db.add_all(batch)
                            await db.flush()  # Send to DB
                            imported += len(batch)
                            logger.debug(f"Processed {imported} records")
                            batch = []
                            
                    except Exception as e:
                        logger.error(f"Error in row {row_num}: {str(e)}")
                        continue
                
                # Process final batch
                if batch:
                    db.add_all(batch)
                    await db.flush()
                    imported += len(batch)
                
                # Transaction will commit automatically when context exits
                
            logger.info(
                f"Import completed - Success: {imported}, Failed: {row_num - imported}, "
                f"Total: {row_num}, Success rate: {(imported/row_num)*100:.2f}%"
            )
            
            return {
                "imported": imported,
                "total": row_num,
                "skipped": row_num - imported,
                "success_rate": f"{(imported/row_num)*100:.2f}%"
            }
            
    except FileNotFoundError:
        error_msg = f"CSV file not found at {filepath}"
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
        
    except HTTPException:
        raise  # Re-raise our own HTTP exceptions
        
    except SQLAlchemyError as e:
        error_msg = f"Database error during import: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during import: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)