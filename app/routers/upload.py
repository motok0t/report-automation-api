from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.report_schemas import FileUploadResponse
from app.services.file_handler import FileHandler

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Загружает CSV или Excel файл и возвращает информацию о данных.
    """
    try:
        df = await FileHandler.read_file(file)
        info = FileHandler.get_file_info(df)

        return FileUploadResponse(
            filename=file.filename,
            rows=info["rows"],
            columns=info["columns"],
            column_names=info["column_names"],
            preview=df.head(5).to_dict(orient="records")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
