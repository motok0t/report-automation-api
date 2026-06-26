from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AggregationType(str, Enum):
    sum = "sum"
    mean = "mean"
    count = "count"
    min = "min"
    max = "max"


class ReportRequest(BaseModel):
    group_by: str
    aggregate_column: str
    aggregation: AggregationType = AggregationType.sum
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None


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
