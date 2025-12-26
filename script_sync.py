import os
import time
from loguru import logger

from utils import *
from fetcher import *


def sync():
    config = utils.load_config()
    pta_session = str(config["fetcher"]["pta_session"])
    problem_set_id = str(config["fetcher"]["problem_set_id"])
    output_dir = str(config["fetcher"]["output_dir"])

    while True:
        logger.info("fetching ranking data...")

        try:
            ranking = fetcher.fetch_common_ranking(pta_session, problem_set_id)
            utils.output(os.path.join(output_dir, "ranking.json"), ranking)
            logger.success("fetch successfully")
        except Exception as e:
            logger.error("fetch failed...")
            logger.error(e)
            
        logger.info("sleep for 15 seconds...")
        time.sleep(15)


if __name__ == "__main__":
    sync()