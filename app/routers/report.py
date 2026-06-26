import pandas as pd
from fastapi import APIRouter, HTTPException

from app.schemas.report_schemas import ReportRequest, ReportResponse
from app.services.data_processor import DataProcessor
from app.utils.validators import validate_aggregation_params

router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/summary", response_model=ReportResponse)
async def generate_summary(request: ReportRequest):
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

        result = DataProcessor.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            request.aggregation.value
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

        return ReportResponse(
            status="success",
            data=data,
            total_rows=len(result),
            summary={
                'total_rows': int(stats['total_rows']),
                'groups': int(stats['groups']),
                'min_value': float(stats['min_value']),
                'max_value': float(stats['max_value']),
                'mean_value': float(stats['mean_value']),
                'std_value': float(stats['std_value'])
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
