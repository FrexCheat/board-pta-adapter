import time

from loguru import logger

from adapter.cli._shared import build_runtime
from adapter.core.xcpcio import XCPCIOAdapter
from common.pta.client import PTAClientError


def _build_runtime():
    return build_runtime(XCPCIOAdapter, lambda config: config.xcpcio.output_dir)


def generate() -> None:
    logger.info("===> starting to generate static data...")
    _, adapter, storage = _build_runtime()
    try:
        logger.info("generating organizations.json...")
        organizations = adapter.get_organizations()
        storage.write_json("organizations.json", [o.model_dump(by_alias=True, exclude_unset=True) for o in organizations])

        logger.info("generating teams.json...")
        teams = adapter.get_teams()
        storage.write_json("teams.json", [t.model_dump(by_alias=True, exclude_unset=True) for t in teams])

        logger.success("===> static data generated successfully.")
    except Exception:
        logger.exception("===> failed to generate static data.")
        raise


def synchronize() -> None:
    logger.info("===> starting to synchronize submissions data...")
    config, adapter, storage = _build_runtime()
    while True:
        try:
            logger.info("generating runs.json...")
            submissions = adapter.get_submissions()
            storage.write_json("runs.json", [s.model_dump() for s in submissions])
            logger.success("===> submissions data synchronized successfully.")
        except PTAClientError:
            logger.exception("===> failed to synchronize submissions data after exhausting PTA retries.")
            raise
        except Exception:
            logger.exception("===> failed to synchronize submissions data.")

        logger.info(f"sleep for {config.sync_interval} seconds before next synchronization...")
        time.sleep(config.sync_interval)
