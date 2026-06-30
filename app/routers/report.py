import logging
import os

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.report_schemas import ReportRequest, ReportResponse
from app.services.data_processor import DataProcessor
from app.utils.validators import validate_aggregation_params


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/summary", response_model=ReportResponse)
async def generate_summary(request: ReportRequest):
    try:
        logger.info(
            f"Generating report: group_by={request.group_by}, "
            f"agg={[a.value for a in request.aggregation]}, "
            f"outliers={request.detect_outliers}"
        )
        df = pd.read_csv("data/homes.csv")
        df = DataProcessor.clean_data(df)

        validate_aggregation_params(
            df,
            request.group_by,
            request.aggregate_column
        )

        if request.filter_column and request.filter_value:
            df = DataProcessor.filter_data(
                df,
                request.filter_column,
                request.filter_value
            )

        if request.detect_outliers:
            df = DataProcessor.detect_outliers(df, request.aggregate_column)

        agg_list = [a.value for a in request.aggregation]
        result = DataProcessor.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            agg_list
        )

        stats = DataProcessor.get_summary_stats(
            df,
            request.group_by,
            request.aggregate_column
        )

        data = result.to_dict(orient="records")
        for row in data:
            for key, value in row.items():
                if hasattr(value, 'item'):
                    row[key] = value.item()

        logger.info(f"Report generated: {len(data)} rows")
        return ReportResponse(
            status="success",
            data=data,
            total_rows=len(result),
            summary=stats
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        logger.error("Data file not found")
        raise HTTPException(status_code=404, detail="Data file not found")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/download/csv")
async def download_csv(request: ReportRequest):
    """Generate report and return as CSV file."""
    try:
        df = pd.read_csv("data/homes.csv")
        df = DataProcessor.clean_data(df)

        validate_aggregation_params(
            df,
            request.group_by,
            request.aggregate_column
        )

        if request.filter_column and request.filter_value:
            df = DataProcessor.filter_data(
                df,
                request.filter_column,
                request.filter_value
            )

        if request.detect_outliers:
            df = DataProcessor.detect_outliers(df, request.aggregate_column)

        agg_list = [a.value for a in request.aggregation]
        result = DataProcessor.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            agg_list
        )

        output_path = "generated_reports/report.csv"
        result.to_csv(output_path, index=False)

        return FileResponse(
            path=output_path,
            filename="report.csv",
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/suggest")
async def suggest_structure(request: ReportRequest):
    """
    Анализирует данные и предлагает колонки для группировки и агрегации.
    """
    try:
        df = pd.read_csv("data/homes.csv")
        df = DataProcessor.clean_data(df)

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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/download/excel")
async def download_excel(request: ReportRequest):
    """Generate report and return as Excel file."""
    try:
        df = pd.read_csv("data/homes.csv")
        df = DataProcessor.clean_data(df)

        validate_aggregation_params(
            df,
            request.group_by,
            request.aggregate_column
        )

        if request.filter_column and request.filter_value:
            df = DataProcessor.filter_data(
                df,
                request.filter_column,
                request.filter_value
            )

        if request.detect_outliers:
            df = DataProcessor.detect_outliers(df, request.aggregate_column)

        agg_list = [a.value for a in request.aggregation]
        result = DataProcessor.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            agg_list
        )

        os.makedirs("generated_reports", exist_ok=True)
        output_path = "generated_reports/report.xlsx"
        result.to_excel(output_path, index=False)

        return FileResponse(
            path=output_path,
            filename="report.xlsx",
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
