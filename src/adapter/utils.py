from pathlib import Path

import pandas as pd
import pendulum


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


def format_ms_to_time(timestamp_ms: int) -> str:
    dt = pendulum.from_timestamp(timestamp_ms / 1000, tz="Asia/Shanghai")
    return dt.format("YYYY-MM-DDTHH:mm:ss.SSSZ")


def calc_ms_time_diff(start_ms: int, end_ms: int) -> str:
    duration = pendulum.duration(milliseconds=end_ms - start_ms)
    return (
        f"{duration.in_hours():02d}:"
        f"{duration.minutes:02d}:"
        f"{duration.remaining_seconds:02d}."
        f"{duration.microseconds // 1000:03d}"
    )


def format_ms_to_clock(timestamp_ms: int) -> str:
    duration = pendulum.duration(milliseconds=timestamp_ms)
    return (
        f"{duration.in_hours()}:"
        f"{duration.minutes:02d}:"
        f"{duration.remaining_seconds:02d}."
        f"{duration.microseconds // 1000:03d}"
    )
