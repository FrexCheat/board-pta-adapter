from pathlib import Path

import pandas as pd


class SheetReader:
    def __init__(self, excel_path: str, sheet_name: str) -> None:
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name
        self._dataframe: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        if self._dataframe is None:
            self._dataframe = pd.read_excel(self.excel_path, sheet_name=self.sheet_name, skiprows=0)
        return self._dataframe

    @staticmethod
    def is_empty(value: object) -> bool:
        if pd.isna(value):
            return True
        if isinstance(value, str):
            return not value.strip()
        return False
