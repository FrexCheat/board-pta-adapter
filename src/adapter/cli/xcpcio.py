import time

from loguru import logger

from adapter.cli.shared import build_runtime
from adapter.core.xcpcio import XCPCIOAdapter
from common.pta.client import PTAClientError


def _build_runtime():
    return build_runtime(XCPCIOAdapter, lambda config: config.xcpcio.output_dir)


def generate() -> None:
    logger.info("===> starting to generate static data...")
    _, adapter, storage = _build_runtime()
    try:
        logger.info("generating config.json...")
        config = adapter.get_config()
        storage.write_json("config.json", config.model_dump())
        storage.write_json("unfrozen-random/config.json", config.model_dump())

        logger.info("generating organizations.json...")
        organizations = adapter.get_organizations()
        storage.write_json(
            "organizations.json", [o.model_dump(by_alias=True, exclude_unset=True) for o in organizations]
        )
        storage.write_json(
            "unfrozen-random/organizations.json",
            [o.model_dump(by_alias=True, exclude_unset=True) for o in organizations],
        )

        logger.info("generating team.json...")
        teams = adapter.get_teams()
        storage.write_json("team.json", [t.model_dump(by_alias=True, exclude_unset=True) for t in teams])
        storage.write_json(
            "unfrozen-random/team.json", [t.model_dump(by_alias=True, exclude_unset=True) for t in teams]
        )

        logger.success("===> static data generated successfully.")
    except Exception:
        logger.exception("===> failed to generate static data.")
        raise


def synchronize() -> None:
    logger.info("===> starting to synchronize submissions data...")
    config, adapter, storage = _build_runtime()
    while True:
        try:
            logger.info("generating run.json...")
            submissions, submissions_unfrozen = adapter.get_submissions()
            storage.write_json("run.json", [s.model_dump() for s in submissions])
            storage.write_json("unfrozen-random/run.json", [s.model_dump() for s in submissions_unfrozen])
            logger.success("===> submissions data synchronized successfully.")
        except PTAClientError:
            logger.exception("===> failed to synchronize submissions data after exhausting PTA retries.")
            raise
        except Exception:
            logger.exception("===> failed to synchronize submissions data.")

        logger.info(f"sleep for {config.sync_interval} seconds before next synchronization...")
        time.sleep(config.sync_interval)
