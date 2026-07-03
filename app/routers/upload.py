import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.report_schemas import FileUploadResponse
from app.services.file_handler import FileHandler


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Uploading file: {file.filename}")
        df = await FileHandler.read_file(file)
        info = FileHandler.get_file_info(df)
        logger.info(f"File uploaded: {file.filename}, rows: {info['rows']}")
        return FileUploadResponse(
            filename=file.filename,
            rows=info["rows"],
            columns=info["columns"],
            column_names=info["column_names"],
            preview=df.head(5).to_dict(orient="records")
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file or data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )
