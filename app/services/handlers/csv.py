import pandas as pd

from app.services.handlers.base import BaseFileHandler


class CSVHandler(BaseFileHandler):
    """Handler for CSV files."""

    def read(self, file_path: str, chunk_size: int = 0) -> pd.DataFrame:
        if chunk_size:
            chunks = []
            for chunk in pd.read_csv(
                file_path,
                quotechar='"',
                chunksize=chunk_size
            ):
                chunks.append(chunk)
            return pd.concat(chunks, ignore_index=True)
        return pd.read_csv(file_path, quotechar='"')

    def save(self, df: pd.DataFrame, file_path: str) -> None:
        df.to_csv(file_path, index=False)
