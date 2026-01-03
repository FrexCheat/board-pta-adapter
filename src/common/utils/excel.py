from pathlib import Path

import pandas as pd


class SheetReader:
    def __init__(self, excel_path: Path, sheet_name: str) -> None:
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self._cache: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        if self._cache is None:
            if not self.excel_path.exists():
                raise FileNotFoundError(f"Excel file not found: {self.excel_path}")

            self._cache = pd.read_excel(self.excel_path, sheet_name=self.sheet_name, skiprows=0)

        return self._cache.copy()
