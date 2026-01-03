from pathlib import Path
from typing import Any, Dict

import yaml

from adapter.models.config import Config


class IConfig:
    @classmethod
    def load(cls, path: str | Path = "config.yml") -> Config:
        config_path = Path(path)
        raw: Dict[str, Any] = yaml.safe_load(config_path.read_text())
        return Config.model_validate(raw)
