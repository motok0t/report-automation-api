import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.report_schemas import ReportRequest
from app.services.aggregator import DataAggregator
from app.services.cleaner import DataCleaner
from app.services.outlier import OutlierDetector
from app.services.utils import get_uploaded_file_path, read_uploaded_file
from app.services.validators import DataValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report/download", tags=["Report"])


@router.post("/csv")
async def download_csv(request: ReportRequest):
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

        DataValidator.validate_aggregation_params(
            df,
            request.group_by,
            request.aggregate_column
        )

        if request.filter_column and request.filter_value:
            df = DataAggregator.filter_data(
                df,
                request.filter_column,
                request.filter_value
            )

        if request.detect_outliers:
            df = OutlierDetector.detect_outliers(df, request.aggregate_column)

        agg_list = [a.value for a in request.aggregation]
        result = DataAggregator.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            agg_list
        )

        if request.sort_by == 'asc':
            result = result.sort_values(by=request.group_by, ascending=True)
        elif request.sort_by == 'desc':
            result = result.sort_values(by=request.group_by, ascending=False)

        os.makedirs("generated_reports", exist_ok=True)
        output_path = "generated_reports/report.csv"
        result.to_csv(output_path, index=False)

        return FileResponse(
            path=output_path,
            filename="report.csv",
            media_type="text/csv"
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
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
