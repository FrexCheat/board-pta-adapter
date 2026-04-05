import json
import shutil
from pathlib import Path
from typing import Any


class OutputStorage:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, filename: str, data: Any) -> Path:
        target = self.base_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=False, ensure_ascii=False)
        return target

    def write_raw(self, filename: str, data: str) -> Path:
        target = self.base_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(data)
        return target

    def mkdir(self, dirname: str) -> Path:
        target = self.base_dir / dirname
        target.mkdir(parents=True, exist_ok=True)
        return target

    def copy(self, src: str, dst: str) -> Path:
        target = self.base_dir / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "rb") as handle_src:
            with target.open("wb") as handle_dst:
                handle_dst.write(handle_src.read())
        return target

    def clear(self) -> None:
        shutil.rmtree(self.base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
