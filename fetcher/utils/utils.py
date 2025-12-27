import json
from datetime import datetime

import yaml


def get_timestamp(dt):
    dt_utc = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    local_tz = datetime.now().astimezone().tzinfo
    dt_local = dt_utc.astimezone(local_tz)
    timestamp = dt_local.timestamp()
    return int(timestamp)


def json_output(data):
    return json.dumps(data, indent=4, sort_keys=False, separators=(",", ": "), ensure_ascii=False)


def output(target_path, data):
    with open(target_path, "w") as f:
        f.write(json_output(data))


def load_config(config_path="config.yml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
