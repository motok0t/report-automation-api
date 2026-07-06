import os
import tempfile
from typing import Any, Dict, List

import pandas as pd
from fastapi import UploadFile

from app.services.handlers.base import BaseFileHandler
from app.services.handlers.csv import CSVHandler
from app.services.handlers.excel import ExcelHandler
from app.services.handlers.json import JSONHandler
from app.services.handlers.parquet import ParquetHandler


class FileHandler:
    """Factory class for file operations."""

    _handlers = {
        '.csv': CSVHandler(),
        '.xlsx': ExcelHandler(),
        '.xls': ExcelHandler(),
        '.json': JSONHandler(),
        '.parquet': ParquetHandler(),
    }

    @staticmethod
    def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Remove quotes and strip whitespace from column names."""
        df.columns = df.columns.str.strip('"').str.strip()
        return df

    @staticmethod
    async def read_file(file: UploadFile) -> pd.DataFrame:
        """Read CSV, Excel, JSON or Parquet file into DataFrame."""
        contents = await file.read()
        suffix = os.path.splitext(file.filename)[1]
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        )
        temp_file.write(contents)
        temp_file.close()

        handler = FileHandler._handlers.get(suffix)
        if handler is None:
            raise ValueError(
                "Unsupported format. Use CSV, Excel, JSON or Parquet."
            )

        df = handler.read(temp_file.name)
        os.unlink(temp_file.name)
        return FileHandler._clean_columns(df)

    @staticmethod
    def read_file_from_path(file_path: str) -> pd.DataFrame:
        """Read CSV, Excel, JSON or Parquet file from path into DataFrame."""
        suffix = os.path.splitext(file_path)[1]
        handler = FileHandler._handlers.get(suffix)
        if handler is None:
            raise ValueError(
                "Unsupported format. Use CSV, Excel, JSON or Parquet."
            )
        df = handler.read(file_path)
        return FileHandler._clean_columns(df)

    @staticmethod
    def save_report(df: pd.DataFrame, filename: str = "report.xlsx") -> str:
        """Save DataFrame to file and return file path."""
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)

        suffix = os.path.splitext(filename)[1]
        handler = FileHandler._handlers.get(suffix, ExcelHandler())
        filepath = os.path.join(output_dir, filename)
        handler.save(df, filepath)
        return filepath

    @staticmethod
    def get_file_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Return rows, columns, dtypes and memory usage of DataFrame."""
        return BaseFileHandler.get_file_info(df)

    @staticmethod
    def get_sheet_names(file: UploadFile) -> List[str]:
        """Return list of sheet names from Excel file."""
        contents = file.file.read()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(contents)
        temp_file.close()
        try:
            sheets = pd.read_excel(temp_file.name, sheet_name=None)
            return list(sheets.keys())
        finally:
            os.unlink(temp_file.name)
