import os
import time

from loguru import logger

from fetcher import utils, worker


def main():
    config = utils.load_config()

    pta_session = str(config["fetcher"]["pta_session"])
    problem_set_id = str(config["fetcher"]["problem_set_id"])
    output_dir = str(config["output_dir"])
    sync_interval = int(config["sync_interval"])

    while True:
        logger.info("fetching ranking data...")

        try:
            ranking = worker.fetch_common_ranking(pta_session, problem_set_id)

            utils.output(os.path.join(output_dir, "ranking.json"), ranking)
            logger.success("fetch successfully")
        except Exception as e:
            logger.error("fetch failed...")
            logger.error(e)

        logger.info(f"sleep for {sync_interval} seconds...")
        time.sleep(sync_interval)


if __name__ == "__main__":
    main()
