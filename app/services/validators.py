from typing import List

import pandas as pd


class DataValidator:
    """Validator for DataFrame structure and types."""

    @staticmethod
    def validate_columns(
        df: pd.DataFrame,
        required_columns: List[str]
    ) -> None:
        """
        Check that all required columns exist in the DataFrame.

        Raises:
            ValueError: If any required column is missing.
        """
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(
                f"Missing columns: {missing}. "
                f"Available: {list(df.columns)}"
            )

    @staticmethod
    def validate_aggregation_params(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str
    ) -> None:
        """
        Check columns exist and aggregate column is numeric.

        Raises:
            ValueError: If columns missing or aggregate column not numeric.
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

    @staticmethod
    def get_column_info(df: pd.DataFrame) -> dict:
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
