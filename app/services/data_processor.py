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
        """
        Агрегирует данные по указанной колонке с несколькими метриками.
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
        return df[df[column] == value]

    @staticmethod
    def get_summary_stats(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str
    ) -> Dict[str, Any]:
        return {
            'total_rows': int(len(df)),
            'groups': int(df[group_by].nunique()),
            'min_value': float(df[aggregate_column].min()),
            'max_value': float(df[aggregate_column].max()),
            'mean_value': float(df[aggregate_column].mean()),
            'std_value': float(df[aggregate_column].std())
        }
