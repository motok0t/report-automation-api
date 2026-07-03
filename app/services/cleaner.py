import pandas as pd


class DataCleaner:
    """Handles data cleaning operations."""

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
