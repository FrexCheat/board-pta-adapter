import time

from loguru import logger

from adapter.core.config import IConfig
from adapter.core.gplt import GPLTAdapter
from common.utils.storage import OutputStorage


def generate() -> None:
    logger.info("===> starting to generate static data...")
    try:
        config = IConfig.load()
        adapter = GPLTAdapter(config)
        storage = OutputStorage(config.gplt.output_dir)

        logger.info("generating contest.json...")
        contest = adapter.get_contest()
        storage.write_json("contest.json", contest.model_dump())

        logger.info("generating students.json...")
        students = adapter.get_students()
        storage.write_json("students.json", [s.model_dump(by_alias=True) for s in students])

        logger.info("generating teams.json...")
        teams = adapter.get_teams()
        storage.write_json("teams.json", [t.model_dump(by_alias=True) for t in teams])

        logger.success("===> static data generated successfully.")
    except Exception as e:
        logger.error("===> failed to generate static data.")
        logger.error(e)


def synchronize() -> None:
    logger.info("===> starting to synchronize rankings data...")

    while True:
        try:
            config = IConfig.load()
            adapter = GPLTAdapter(config)
            storage = OutputStorage(config.gplt.output_dir)

            logger.info("generating rankings.json...")
            rankings = adapter.get_rankings()
            storage.write_json("rankings.json", [r.model_dump() for r in rankings])

            logger.success("===> rankings data synchronized successfully.")
        except Exception as e:
            logger.error("===> failed to synchronize rankings data.")
            logger.error(e)

        logger.info(f"sleep for {config.sync_interval} seconds before next synchronization...")
        time.sleep(config.sync_interval)
