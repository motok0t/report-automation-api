import pandas as pd

from app.services.handlers.base import BaseFileHandler


class ExcelHandler(BaseFileHandler):
    """Handler for Excel files."""

    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path)

    def save(self, df: pd.DataFrame, file_path: str) -> None:
        df.to_excel(file_path, index=False)
