from typing import Any, Dict, List

import pandas as pd


class DataAggregator:
    """Handles data aggregation and statistics."""

    @staticmethod
    def aggregate_data(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str,
        aggregations: List[str]
    ) -> pd.DataFrame:
        """
        Aggregate data by specified column with multiple metrics.
        """
        grouped = df.groupby(group_by)[aggregate_column]
        result = grouped.agg(aggregations).reset_index()

        for col in result.columns:
            dtype = result[col].dtype.name
            if dtype.startswith('int'):
                result[col] = result[col].astype('int64')
            elif dtype.startswith('float'):
                result[col] = result[col].astype('float64')

        return result

    @staticmethod
    def filter_data(
        df: pd.DataFrame,
        column: str,
        value: Any
    ) -> pd.DataFrame:
        """Filter DataFrame by column value."""
        return df[df[column] == value]

    @staticmethod
    def get_summary_stats(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str,
        detect_outliers: bool = False
    ) -> Dict[str, Any]:
        """
        Return summary statistics with optional outlier detection.
        """
        stats = {
            'total_rows': int(len(df)),
            'groups': int(df[group_by].nunique()),
            'min_value': float(df[aggregate_column].min()),
            'max_value': float(df[aggregate_column].max()),
            'mean_value': float(df[aggregate_column].mean()),
            'std_value': float(df[aggregate_column].std())
        }

        if detect_outliers:
            mean = df[aggregate_column].mean()
            std = df[aggregate_column].std()
            lower_bound = mean - 2 * std
            upper_bound = mean + 2 * std
            has_outliers = (
                (df[aggregate_column] < lower_bound) |
                (df[aggregate_column] > upper_bound)
            ).any()
            stats['has_outliers'] = bool(has_outliers)

        return stats
