from typing import Any, Dict, List

import pandas as pd


class DataProcessor:
    """Класс для обработки данных: очистка и агрегация."""

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
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
        return df[df[column] == value]

    @staticmethod
    def get_summary_stats(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str
    ) -> Dict[str, Any]:
        mean = df[aggregate_column].mean()
        std = df[aggregate_column].std()
        lower_bound = mean - 2 * std
        upper_bound = mean + 2 * std
        has_outliers = (
            (df[aggregate_column] < lower_bound) |
            (df[aggregate_column] > upper_bound)
        ).any()

        return {
            'total_rows': int(len(df)),
            'groups': int(df[group_by].nunique()),
            'min_value': float(df[aggregate_column].min()),
            'max_value': float(df[aggregate_column].max()),
            'mean_value': float(mean),
            'std_value': float(std),
            'has_outliers': bool(has_outliers)
        }

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        aggregate_column: str,
        threshold: float = 2.0
    ) -> pd.DataFrame:
        mean = df[aggregate_column].mean()
        std = df[aggregate_column].std()
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
        df['is_outlier'] = (
            (df[aggregate_column] < lower_bound) |
            (df[aggregate_column] > upper_bound)
        )
        return df
