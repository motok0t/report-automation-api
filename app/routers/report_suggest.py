import logging

from fastapi import APIRouter, HTTPException

from app.schemas.report_schemas import ReportRequest
from app.services.cleaner import DataCleaner
from app.services.utils import get_uploaded_file_path, read_uploaded_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/suggest")
async def suggest_structure(request: ReportRequest):
    try:
        file_path = get_uploaded_file_path()
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="No file uploaded yet."
            )

        if request.sheet_name and file_path.endswith(('.xlsx', '.xls')):
            df = read_uploaded_file(file_path, sheet_name=request.sheet_name)
        else:
            df = read_uploaded_file(file_path)

        df.columns = df.columns.str.replace('"', '').str.strip()
        df = DataCleaner.clean_data(df)

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = (
            df.select_dtypes(include=['object', 'category'])
            .columns.tolist()
        )

        return {
            "categorical_columns": categorical_cols,
            "numeric_columns": numeric_cols,
            "suggested_group_by": (
                categorical_cols[:3] if categorical_cols else []
            ),
            "suggested_aggregate": (
                numeric_cols[:3] if numeric_cols else []
            )
        }
    except FileNotFoundError:
        logger.error("Data file not found")
        raise HTTPException(
            status_code=404,
            detail="Data file not found. Please upload a file first."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )
