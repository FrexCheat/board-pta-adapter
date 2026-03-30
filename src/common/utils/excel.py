from pathlib import Path

import pandas as pd


class SheetReader:
    def __init__(self, excel_path: str, sheet_name: str) -> None:
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name

    def load(self) -> pd.DataFrame:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        return pd.read_excel(self.excel_path, sheet_name=self.sheet_name, skiprows=0)

    @staticmethod
    def is_empty(value):
        if pd.isna(value):
            return True
        if isinstance(value, str):
            return not value.strip()
        return False
