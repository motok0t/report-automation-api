import logging
import os
from math import isfinite

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.report_schemas import ReportRequest, ReportResponse
from app.services.aggregator import DataAggregator
from app.services.cleaner import DataCleaner
from app.services.outlier import OutlierDetector
from app.services.validators import DataValidator


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])


def clean_inf_from_dict(data):
    """Recursively replace inf, -inf with None in dict/list."""
    if isinstance(data, dict):
        return {k: clean_inf_from_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_inf_from_dict(item) for item in data]
    if isinstance(data, float) and (not isfinite(data) or data != data):
        return None
    return data


@router.post("/summary", response_model=ReportResponse)
async def generate_summary(request: ReportRequest):
    """Generate aggregated report with summary statistics."""
    try:
        logger.info(
            f"Generating report: group_by={request.group_by}, "
            f"agg={[a.value for a in request.aggregation]}, "
            f"outliers={request.detect_outliers}, "
            f"sheet={request.sheet_name}, "
            f"sort={request.sort_by}"
        )

        if request.sheet_name:
            df = pd.read_excel(
                "uploaded_files/sampledatafoodsales.xlsx",
                sheet_name=request.sheet_name,
                engine='openpyxl'
            )
        else:
            df = pd.read_csv("data/homes.csv")

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

        if request.detect_outliers:
            outliers_by_group = (
                df.groupby(request.group_by)['is_outlier'].any()
            )
            result['has_outliers'] = (
                result[request.group_by].map(outliers_by_group)
            )

        stats = DataAggregator.get_summary_stats(
            df,
            request.group_by,
            request.aggregate_column,
            request.detect_outliers
        )

        data = result.to_dict(orient="records")
        for row in data:
            for key, value in row.items():
                if hasattr(value, 'item'):
                    row[key] = value.item()

        data = clean_inf_from_dict(data)
        stats = clean_inf_from_dict(stats)

        logger.info(f"Report generated: {len(data)} rows")
        return ReportResponse(
            status="success",
            data=data,
            total_rows=len(result),
            summary=stats
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
            detail=(
                "Data file not found. "
                "Check that 'data/homes.csv' exists."
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )


@router.post("/download/csv")
async def download_csv(request: ReportRequest):
    """Generate report and return as CSV file."""
    try:
        if request.sheet_name:
            df = pd.read_excel(
                "uploaded_files/sampledatafoodsales.xlsx",
                sheet_name=request.sheet_name,
                engine='openpyxl'
            )
        else:
            df = pd.read_csv("data/homes.csv")

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
            detail=(
                "Data file not found. "
                "Check that 'data/homes.csv' exists."
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )


@router.post("/suggest")
async def suggest_structure(request: ReportRequest):
    """
    Analyze data and suggest columns for grouping and aggregation.
    """
    try:
        if request.sheet_name:
            df = pd.read_excel(
                "uploaded_files/sampledatafoodsales.xlsx",
                sheet_name=request.sheet_name,
                engine='openpyxl'
            )
        else:
            df = pd.read_csv("data/homes.csv")

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
            detail=(
                "Data file not found. "
                "Check that 'data/homes.csv' exists."
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )


@router.post("/download/excel")
async def download_excel(request: ReportRequest):
    """Generate report and return as Excel file with highlighted outliers."""
    try:
        if request.sheet_name:
            df = pd.read_excel(
                "uploaded_files/sampledatafoodsales.xlsx",
                sheet_name=request.sheet_name,
                engine='openpyxl'
            )
        else:
            df = pd.read_csv("data/homes.csv")

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

        if request.detect_outliers:
            result = OutlierDetector.highlight_outliers(result, 'sum')
            result = result.drop(columns=['_style'], errors='ignore')

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
            detail=(
                "Data file not found. "
                "Check that 'data/homes.csv' exists."
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )
