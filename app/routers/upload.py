import logging
import os
from math import isfinite

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.report_schemas import FileUploadResponse
from app.services.file_handler import FileHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

_current_file_path = None


@router.post("/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    global _current_file_path
    try:
        logger.info(f"Uploading file: {file.filename}")
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        _current_file_path = file_path

        df = FileHandler.read_file_from_path(file_path)
        info = FileHandler.get_file_info(df)

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = (
            df.select_dtypes(include=['object', 'category'])
            .columns.tolist()
        )

        logger.info(f"File uploaded: {file.filename}, rows: {info['rows']}")
        return FileUploadResponse(
            filename=file.filename,
            rows=info["rows"],
            columns=info["columns"],
            column_names=info["column_names"],
            preview=df.head(5).to_dict(orient="records"),
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols
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


@router.get("/sheets")
async def get_sheets():
    if _current_file_path is None:
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    try:
        sheets = pd.read_excel(
            _current_file_path,
            sheet_name=None,
            engine='openpyxl'
        )
        return {"sheets": list(sheets.keys())}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading sheets: {str(e)}"
        )


@router.get("/columns")
async def get_columns(sheet: str):
    if _current_file_path is None:
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    try:
        df = pd.read_excel(
            _current_file_path,
            sheet_name=sheet,
            nrows=1,
            engine='openpyxl',
            header=0
        )
        df.columns = [str(col).replace('"', '').strip() for col in df.columns]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = (
            df.select_dtypes(include=['object', 'category'])
            .columns.tolist()
        )
        return {
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading columns: {str(e)}"
        )


def clean_inf_from_dict(data):
    if isinstance(data, dict):
        return {k: clean_inf_from_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_inf_from_dict(item) for item in data]
    if isinstance(data, float) and (not isfinite(data) or data != data):
        return None
    return data


@router.get("/preview")
async def get_preview(sheet: str):
    if _current_file_path is None:
        raise HTTPException(status_code=404, detail="No file uploaded yet.")
    try:
        df = pd.read_excel(
            _current_file_path,
            sheet_name=sheet,
            engine='openpyxl',
            header=0
        )
        df.columns = [str(col).replace('"', '').strip() for col in df.columns]
        preview = df.head(5).to_dict(orient="records")
        preview = clean_inf_from_dict(preview)
        return {"preview": preview}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading preview: {str(e)}"
        )
