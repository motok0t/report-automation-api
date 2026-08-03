from abc import ABC, abstractmethod
from typing import Any, Dict

import pandas as pd


class BaseFileHandler(ABC):
    """Abstract base class for file handlers."""

    @abstractmethod
    def read(self, file_path: str) -> pd.DataFrame:
        """Read file into DataFrame."""
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame to file."""
        pass

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
