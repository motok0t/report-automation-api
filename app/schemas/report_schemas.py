from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AggregationType(str, Enum):
    SUM = "sum"
    MEAN = "mean"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class ReportRequest(BaseModel):
    group_by: str
    aggregate_column: str
    aggregation: List[AggregationType] = [AggregationType.SUM]
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None
    detect_outliers: bool = False


class ReportResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    total_rows: int
    summary: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    preview: List[Dict[str, Any]]
