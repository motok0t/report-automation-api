from typing import Any, Dict, List

import pandas as pd


class DataProcessor:
    """Data cleaning and aggregation utilities."""

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data by removing duplicates and filling missing values.
        """
        df = df.drop_duplicates()
        df = df.dropna(how='all')

        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna('unknown')

        return df

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

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        aggregate_column: str,
        threshold: float = 2.0
    ) -> pd.DataFrame:
        """
        Add is_outlier column to DataFrame.

        Marks rows where value deviates more than threshold * std from mean.
        """
        mean = df[aggregate_column].mean()
        std = df[aggregate_column].std()
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
        df['is_outlier'] = (
            (df[aggregate_column] < lower_bound) |
            (df[aggregate_column] > upper_bound)
        )
        return df
