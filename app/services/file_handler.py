import os
import tempfile
from typing import Any, Dict

import pandas as pd
from fastapi import UploadFile


class FileHandler:
    """Класс для работы с загруженными файлами."""

    @staticmethod
    async def read_file(file: UploadFile) -> pd.DataFrame:
        """Читает CSV или Excel файл в pandas DataFrame."""
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
        else:
            raise ValueError(
                "Unsupported format. Use CSV or Excel."
            )

        os.unlink(temp_file.name)
        return df

    @staticmethod
    def save_report(df: pd.DataFrame, filename: str = "report.xlsx") -> str:
        """Сохраняет DataFrame в Excel и возвращает путь."""
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        df.to_excel(filepath, index=False)
        return filepath

    @staticmethod
    def get_file_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Возвращает информацию о DataFrame."""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
