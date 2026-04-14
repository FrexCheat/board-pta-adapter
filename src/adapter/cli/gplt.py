import time

from loguru import logger

from adapter.cli.shared import build_runtime
from adapter.core.gplt import GPLTAdapter
from common.pta.client import PTAClientError


def _build_runtime():
    return build_runtime(GPLTAdapter, lambda config: config.gplt.output_dir)


def generate() -> None:
    logger.info("===> starting to generate static data...")
    _, adapter, storage = _build_runtime()
    try:
        logger.info("generating contest.json...")
        contest = adapter.get_contest()
        storage.write_json("contest.json", contest.model_dump())

        logger.info("generating students.json...")
        students = adapter.get_students()
        storage.write_json("students.json", [s.model_dump(by_alias=True, exclude_none=True) for s in students])

        logger.info("generating teams.json...")
        teams = adapter.get_teams()
        storage.write_json("teams.json", [t.model_dump(by_alias=True, exclude_none=True) for t in teams])

        logger.success("===> static data generated successfully.")
    except Exception:
        logger.exception("===> failed to generate static data.")
        raise


def synchronize() -> None:
    logger.info("===> starting to synchronize rankings data...")
    config, adapter, storage = _build_runtime()
    while True:
        try:
            logger.info("generating rankings.json...")
            rankings = adapter.get_rankings()
            storage.write_json("rankings.json", [r.model_dump() for r in rankings])
            logger.success("===> rankings data synchronized successfully.")
        except PTAClientError:
            logger.exception("===> failed to synchronize rankings data after exhausting PTA retries.")
            raise
        except Exception:
            logger.exception("===> failed to synchronize rankings data.")

        logger.info(f"sleep for {config.sync_interval} seconds before next synchronization...")
        time.sleep(config.sync_interval)
