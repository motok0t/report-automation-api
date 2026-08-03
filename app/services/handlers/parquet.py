import pandas as pd

from app.services.handlers.base import BaseFileHandler


class ParquetHandler(BaseFileHandler):
    """Handler for Parquet files."""

    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_parquet(file_path)

    def save(self, df: pd.DataFrame, file_path: str) -> None:
        df.to_parquet(file_path, index=False)
