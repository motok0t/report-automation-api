from typing import Any, Dict

import pandas as pd


class DataProcessor:
    """Класс для обработки данных: очистка и агрегация."""

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Выполняет базовую очистку данных:
        - Удаление дубликатов
        - Заполнение пропусков в числах (медианой)
        - Заполнение пропусков в строках ('unknown')
        - Удаление пустых строк
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
        aggregation: str = 'sum'
    ) -> pd.DataFrame:
        """
        Агрегирует данные по указанной колонке.
        """
        grouped = df.groupby(group_by)[aggregate_column]

        if aggregation == 'sum':
            result = grouped.sum().reset_index()
        elif aggregation == 'mean':
            result = grouped.mean().reset_index()
        elif aggregation == 'count':
            result = grouped.count().reset_index()
        elif aggregation == 'min':
            result = grouped.min().reset_index()
        elif aggregation == 'max':
            result = grouped.max().reset_index()
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")

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
        """Фильтрует данные по значению."""
        return df[df[column] == value]

    @staticmethod
    def get_summary_stats(
        df: pd.DataFrame,
        group_by: str,
        aggregate_column: str
    ) -> Dict[str, Any]:
        """Возвращает сводную статистику."""
        return {
            'total_rows': len(df),
            'groups': df[group_by].nunique(),
            'min_value': df[aggregate_column].min(),
            'max_value': df[aggregate_column].max(),
            'mean_value': df[aggregate_column].mean(),
            'std_value': df[aggregate_column].std()
        }
