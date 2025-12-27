import os

import pandas as pd
from loguru import logger

from fetcher import utils, worker


def generate_contest():
    logger.info("generating contest info...")

    config = utils.load_config()

    pta_session = str(config["fetcher"]["pta_session"])
    problem_set_id = str(config["fetcher"]["problem_set_id"])
    output_dir = str(config["output_dir"])

    try:
        _contest_info = {}
        problem_set_info = worker.fetch_problem_set_info(pta_session, problem_set_id)
        problem_list = worker.fetch_problem_list(pta_session, problem_set_id)
        _contest_info["title"] = str(problem_set_info["name"])
        _contest_info["standard_1"] = int(config["contest"]["standard_1"])
        _contest_info["standard_2"] = int(config["contest"]["standard_2"])
        _contest_info["problems"] = problem_list

        utils.output(os.path.join(output_dir, "contest.json"), _contest_info)

        logger.success("contest info generate successfully")
    except Exception as e:
        logger.error("contest info generate failed...")
        logger.error(e)


def generate_students():
    logger.info("generating students info...")

    config = utils.load_config()

    output_dir = str(config["output_dir"])
    excel_dir = str(config["generator"]["excel_dir"])
    excel_name = str(config["generator"]["excel_name"])
    sheet_name = str(config["generator"]["sheet_name"])

    try:
        file_path = os.path.join(excel_dir, excel_name)
        source = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=0)

        df = source.iloc[:, [0, 1, 2, 3, 5, 6]].copy()
        df.columns = ["id", "team_id", "name", "school", "college", "class"]
        df["id"] = df["id"].astype(str)
        df["team_id"] = df["team_id"].astype(str)
        df["name"] = df["name"].astype(str).str.strip()

        output = df.to_dict(orient="records")
        utils.output(os.path.join(output_dir, "students.json"), output)

        logger.success("students info generate successfully")
    except Exception as e:
        logger.error("students info generate failed...")
        logger.error(e)


def generate_teams():
    logger.info("generating teams info...")

    config = utils.load_config()

    output_dir = str(config["output_dir"])
    excel_dir = str(config["generator"]["excel_dir"])
    excel_name = str(config["generator"]["excel_name"])
    sheet_name = str(config["generator"]["sheet_name"])

    try:
        file_path = os.path.join(excel_dir, excel_name)
        source = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=0)

        df = source.iloc[:, [1, 4, 3, 5, 6]].copy()
        df.columns = ["id", "name", "school", "college", "class"]

        _teams = {}
        for _, row in df.iterrows():
            team_id = row["id"]
            if team_id not in _teams:
                _teams[team_id] = {
                    "id": str(team_id),
                    "name": row["name"],
                    "school": row["school"],
                    "college": row["college"],
                    "class": row["class"],
                }

        output = list(_teams.values())
        utils.output(os.path.join(output_dir, "teams.json"), output)

        logger.success("teams info generate successfully")
    except Exception as e:
        logger.error("teams info generate failed...")
        logger.error(e)


def main():
    generate_contest()
    generate_students()
    generate_teams()


if __name__ == "__main__":
    main()
