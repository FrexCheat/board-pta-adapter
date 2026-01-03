import json
from pathlib import Path
from typing import Any


class OutputStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, filename: str, data: Any) -> Path:
        target = self.base_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=False, ensure_ascii=False)
        return target
