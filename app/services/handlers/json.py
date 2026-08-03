import json

import pandas as pd

from app.services.handlers.base import BaseFileHandler


class JSONHandler(BaseFileHandler):
    """Handler for JSON files."""

    def read(self, file_path: str) -> pd.DataFrame:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def save(self, df: pd.DataFrame, file_path: str) -> None:
        df.to_json(file_path, orient='records', indent=2)
