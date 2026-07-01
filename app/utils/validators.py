from typing import Any, Dict, List

import pandas as pd


def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Check that all required columns exist in the DataFrame.
    """
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"Column '{col}' not found. "
                f"Available: {list(df.columns)}"
            )
    return True


def validate_aggregation_params(
    df: pd.DataFrame,
    group_by: str,
    aggregate_column: str
) -> bool:
    """
    Check that columns exist and aggregate column is numeric.
    """
    if group_by not in df.columns:
        raise ValueError(f"Group by column '{group_by}' not found.")
    if aggregate_column not in df.columns:
        raise ValueError(
            f"Aggregate column '{aggregate_column}' not found."
        )

    if not pd.api.types.is_numeric_dtype(df[aggregate_column]):
        raise ValueError(
            f"Aggregate column '{aggregate_column}' must be numeric."
        )

    return True


def get_column_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return column info: dtype, null count, unique count, sample values.
    """
    info = {}
    for col in df.columns:
        info[col] = {
            "dtype": str(df[col].dtype),
            "nulls": int(df[col].isnull().sum()),
            "unique": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).tolist()
        }
    return info
