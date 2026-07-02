import pandas as pd

from app.services.handlers.base import BaseFileHandler


class CSVHandler(BaseFileHandler):
    """Handler for CSV files."""

    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def save(self, df: pd.DataFrame, file_path: str) -> None:
        df.to_csv(file_path, index=False)
