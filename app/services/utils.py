import logging
import os
from math import isfinite

import pandas as pd

logger = logging.getLogger(__name__)


def clean_inf_from_dict(data):
    """Recursively replace inf, -inf with None in dict/list."""
    if isinstance(data, dict):
        return {k: clean_inf_from_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_inf_from_dict(item) for item in data]
    if isinstance(data, float) and (not isfinite(data) or data != data):
        return None
    return data


def get_uploaded_file_path():
    """Get the most recently uploaded file path."""
    upload_dir = "uploaded_files"
    files = os.listdir(upload_dir)
    if not files:
        return None
    return os.path.join(upload_dir, files[-1])


def read_uploaded_file(file_path: str, sheet_name: str = "") -> pd.DataFrame:
    """Read uploaded file based on extension."""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        return pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            engine='openpyxl'
        )
    elif file_path.endswith('.parquet'):
        return pd.read_parquet(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
