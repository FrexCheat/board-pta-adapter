import time

from loguru import logger

from adapter.config import IConfig
from adapter.core.xcpcio import XCPCIOAdapter
from common.utils.storage import OutputStorage


def ____init____():
    try:
        config = IConfig.load()
        adapter = XCPCIOAdapter(config)
        storage = OutputStorage(config.xcpcio.output_dir)
    except Exception as e:
        logger.error("===> failed to initialize loader.")
        logger.error(e)
        raise
    return config, adapter, storage


def generate() -> None:
    logger.info("===> starting to generate static data...")
    config, adapter, storage = ____init____()
    try:
        logger.info("generating organizations.json...")
        organizations = adapter.get_organizations()
        storage.write_json("organizations.json", [o.model_dump(by_alias=True, exclude_unset=True) for o in organizations])

        logger.info("generating teams.json...")
        teams = adapter.get_teams()
        storage.write_json("teams.json", [t.model_dump(by_alias=True, exclude_unset=True) for t in teams])

        logger.success("===> static data generated successfully.")
    except Exception as e:
        logger.error("===> failed to generate static data.")
        logger.error(e)


def synchronize() -> None:
    logger.info("===> starting to synchronize submissions data...")
    config, adapter, storage = ____init____()
    while True:
        try:
            logger.info("generating runs.json...")
            submissions = adapter.get_submissions()
            storage.write_json("runs.json", [s.model_dump() for s in submissions])

            logger.success("===> submissions data synchronized successfully.")
        except Exception as e:
            logger.error("===> failed to synchronize submissions data.")
            logger.error(e)

        logger.info(f"sleep for {config.sync_interval} seconds before next synchronization...")
        time.sleep(config.sync_interval)
