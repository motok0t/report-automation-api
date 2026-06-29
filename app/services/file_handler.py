import json
import os
import tempfile
from typing import Any, Dict

import pandas as pd
from fastapi import UploadFile


class FileHandler:
    """File upload and processing utilities."""

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

        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_file.name)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(temp_file.name)
        elif file.filename.endswith('.json'):
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        elif file.filename.endswith('.parquet'):
            df = pd.read_parquet(temp_file.name)
        else:
            raise ValueError(
                "Unsupported format. Use CSV, Excel, JSON or Parquet."
            )

        os.unlink(temp_file.name)
        return df

    @staticmethod
    def save_report(df: pd.DataFrame, filename: str = "report.xlsx") -> str:
        """Save DataFrame to Excel file and return file path."""
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
        return filepath

    @staticmethod
    def get_file_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Return rows, columns, dtypes and memory usage of DataFrame."""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
