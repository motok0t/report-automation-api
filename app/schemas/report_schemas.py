from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AggregationType(str, Enum):
    """Supported aggregation functions."""
    SUM = "sum"
    MEAN = "mean"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class ReportRequest(BaseModel):
    """Request model for report generation."""
    group_by: str
    aggregate_column: str
    aggregation: List[AggregationType] = [AggregationType.SUM]
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None
    detect_outliers: bool = False
    sheet_name: Optional[str] = None
    sort_by: Optional[str] = None
    outlier_metric: Optional[str] = None


class ReportResponse(BaseModel):
    """Response model containing report data and summary."""
    status: str
    data: List[Dict[str, Any]]
    total_rows: int
    summary: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    preview: List[Dict[str, Any]]
    numeric_columns: List[str] = []
    categorical_columns: List[str] = []
