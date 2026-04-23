import json
import time
from pathlib import Path

from loguru import logger

from adapter.config import load_config
from adapter.core.gplt import GPLTAdapter
from adapter.pta_client import PTAClientError


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _build_runtime():
    config = load_config()
    adapter = GPLTAdapter(config)
    output_dir = Path(config.gplt.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return config, adapter, output_dir


def generate() -> None:
    logger.info("===> starting to generate static data...")
    _, adapter, output_dir = _build_runtime()

    logger.info("generating contest.json...")
    contest = adapter.get_contest()
    _write_json(output_dir / "contest.json", contest.model_dump())

    logger.info("generating students.json...")
    students = adapter.get_students()
    _write_json(output_dir / "students.json", [s.model_dump(by_alias=True, exclude_none=True) for s in students])

    logger.info("generating teams.json...")
    teams = adapter.get_teams()
    _write_json(output_dir / "teams.json", [t.model_dump(by_alias=True, exclude_none=True) for t in teams])

    logger.success("===> static data generated successfully.")


def synchronize() -> None:
    logger.info("===> starting to synchronize rankings data...")
    config, adapter, output_dir = _build_runtime()
    while True:
        try:
            logger.info("generating rankings.json...")
            rankings = adapter.get_rankings()
            _write_json(output_dir / "rankings.json", [ranking.model_dump() for ranking in rankings])
            logger.success("===> rankings data synchronized successfully.")
        except PTAClientError:
            logger.exception("PTA API unreachable, will retry next cycle.")
        except Exception:
            logger.exception("unexpected error during sync, crashing.")
            raise

        logger.info("sleep for {} seconds before next synchronization...", config.sync_interval)
        time.sleep(config.sync_interval)
