import json

import pendulum
from loguru import logger

from adapter.cli.shared import build_runtime
from adapter.core.xcpcio import XCPCIOAdapter

JUDGEMENT_ID_MAPPING = {
    "ACCEPTED": "AC",
    "WRONG_ANSWER": "WA",
    "COMPILATION_ERROR": "CE",
    "RUNTIME_ERROR": "RTE",
    "TIME_LIMIT_EXCEEDED": "TLE",
    "MEMORY_LIMIT_EXCEEDED": "MLE",
    "OUTPUT_LIMIT_EXCEEDED": "OLE",
    "PRESENTATION_ERROR": "PE",
}

LANGUAGE_MAPPING = {
    "C": "C",
    "CPP": "C++",
    "Python": "Python",
    "JAVAC": "Java",
}

LANGUAGE_REVERSE_MAPPING = {v: k for k, v in LANGUAGE_MAPPING.items()}


def _build_runtime():
    return build_runtime(XCPCIOAdapter, lambda config: config.cdp.output_dir)


def format_ms_to_time(ts):
    dt = pendulum.from_timestamp(ts / 1000, tz="Asia/Shanghai")
    result = dt.format("YYYY-MM-DDTHH:mm:ss.SSSZ")
    return result


def calc_ms_time_diff(ts1, ts2):
    diff = pendulum.duration(milliseconds=ts2 - ts1)
    return f"{diff.in_hours():02d}:{diff.minutes:02d}:{diff.remaining_seconds:02d}.{diff.microseconds // 1000:03d}"


def format_ms_to_clock(ts):
    d = pendulum.duration(milliseconds=ts)
    return f"{d.in_hours()}:{d.minutes:02d}:{d.remaining_seconds:02d}.{d.microseconds // 1000:03d}"


def get_judgement_type(id: str, name: str, penalty: bool, solved: bool, token: str) -> dict:
    return {
        "type": "judgement-types",
        "id": id,
        "data": {"id": id, "name": name, "penalty": penalty, "solved": solved},
        "token": token,
    }


def get_language(id: str, name: str, token: str) -> dict:
    return {
        "type": "languages",
        "id": id,
        "data": {"id": id, "name": name, "entry_point_required": False},
        "token": token,
    }


def generate() -> None:
    logger.info("===> starting to generate contest data package...")
    config, adapter, storage = _build_runtime()
    try:
        storage.clear()
        storage.mkdir("organizations")

        state = {}
        state["type"] = "state"
        stateData = {}
        stateData["started"] = format_ms_to_time(config.xcpcio.config.start_time)
        stateData["ended"] = format_ms_to_time(config.xcpcio.config.end_time)
        stateData["frozen"] = format_ms_to_time(
            config.xcpcio.config.end_time - (config.xcpcio.config.frozen_time * 1000)
        )
        stateData["thawed"] = None
        stateData["finalized"] = format_ms_to_time(config.xcpcio.config.end_time + (120 * 1000))
        stateData["end_of_updates"] = format_ms_to_time(config.xcpcio.config.end_time + (150 * 1000))
        state["data"] = stateData
        state["token"] = "t0"
        storage.write_raw("event-feed.ndjson", json.dumps(state, ensure_ascii=False) + "\n")

        contest = {}
        contest["type"] = "contest"
        contest["id"] = config.pta.problem_set_id
        contestData = {}
        contestData["id"] = config.pta.problem_set_id
        contestData["name"] = config.xcpcio.config.contest_name
        contestData["formal_name"] = config.xcpcio.config.contest_name
        contestData["start_time"] = format_ms_to_time(config.xcpcio.config.start_time)
        contestData["duration"] = calc_ms_time_diff(config.xcpcio.config.start_time, config.xcpcio.config.end_time)
        contestData["scoreboard_type"] = "pass-fail"
        contestData["scoreboard_freeze_duration"] = calc_ms_time_diff(0, config.xcpcio.config.frozen_time * 1000)
        contestData["penalty_time"] = int(config.xcpcio.config.penalty / 60)
        contest["data"] = contestData
        contest["token"] = "t1"
        storage.write_raw("event-feed.ndjson", json.dumps(contest, ensure_ascii=False) + "\n")

        i = 2
        for name, id in JUDGEMENT_ID_MAPPING.items():
            judgement_type = get_judgement_type(
                id, name, penalty=(id != "AC" and id != "CE"), solved=(id == "AC"), token=f"t{i}"
            )
            storage.write_raw("event-feed.ndjson", json.dumps(judgement_type, ensure_ascii=False) + "\n")
            i += 1

        for id, name in LANGUAGE_MAPPING.items():
            language = get_language(id, name, token=f"t{i}")
            storage.write_raw("event-feed.ndjson", json.dumps(language, ensure_ascii=False) + "\n")
            i += 1

        _problems = adapter.pta_client.fetch_problem_types()
        for p in _problems.labels:
            problem_data = {
                "id": p.problemPoolIndex - 1,
                "name": p.title,
                "label": p.label,
                "ordinal": p.problemPoolIndex,
                "rgb": config.xcpcio.config.balloon_color[p.problemPoolIndex - 1],
            }
            problem = {
                "type": "problems",
                "id": p.problemPoolIndex - 1,
                "data": problem_data,
                "token": f"t{i}",
            }
            storage.write_raw("event-feed.ndjson", json.dumps(problem, ensure_ascii=False) + "\n")
            i += 1

        for id, name in config.xcpcio.config.group.items():
            group = {
                "type": "groups",
                "id": id,
                "data": {"id": id, "name": name},
                "token": f"t{i}",
            }
            storage.write_raw("event-feed.ndjson", json.dumps(group, ensure_ascii=False) + "\n")
            i += 1

        _organizations = adapter.get_organizations(False)
        for organization in _organizations:
            org = {
                "type": "organizations",
                "id": organization.id,
                "data": {"id": organization.id, "name": organization.name, "formal_name": organization.name},
                "token": f"t{i}",
            }
            storage.mkdir(f"organizations/{organization.id}")
            storage.copy(f"./output/logos/{organization.id}.png", f"organizations/{organization.id}/logo.png")
            storage.write_raw("event-feed.ndjson", json.dumps(org, ensure_ascii=False) + "\n")
            i += 1

        _teams = adapter.get_teams(False)
        for team in _teams:
            team_data = {
                "id": team.id,
                "label": team.id,
                "name": team.name,
                "display_name": team.name,
                "organization_id": team.organization_id,
                "group_ids": team.group,
            }
            team_event = {
                "type": "teams",
                "id": team.id,
                "data": team_data,
                "token": f"t{i}",
            }
            storage.write_raw("event-feed.ndjson", json.dumps(team_event, ensure_ascii=False) + "\n")
            i += 1

        _submissions = adapter.get_submissions(is_frozen=False)
        for submission in _submissions:
            submission_data = {
                "id": submission.id,
                "team_id": submission.team_id,
                "problem_id": submission.problem_id,
                "language_id": LANGUAGE_REVERSE_MAPPING.get(submission.language, "UNKNOWN"),
                "time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "contest_time": calc_ms_time_diff(0, submission.timestamp),
            }
            submission_event = {
                "type": "submissions",
                "id": submission.id,
                "data": submission_data,
                "token": f"t{i}",
            }
            storage.write_raw("event-feed.ndjson", json.dumps(submission_event, ensure_ascii=False) + "\n")
            i += 1
            judgement_data = {
                "id": f"j-{submission.id}",
                "submission_id": submission.id,
                "judgement_type_id": JUDGEMENT_ID_MAPPING.get(submission.status, "UNKNOWN"),
                "start_time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "start_contest_time": calc_ms_time_diff(0, submission.timestamp),
                "end_time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "end_contest_time": calc_ms_time_diff(0, submission.timestamp),
            }
            judgement_event = {
                "type": "judgements",
                "id": f"j-{submission.id}",
                "data": judgement_data,
                "token": f"t{i}",
            }
            storage.write_raw("event-feed.ndjson", json.dumps(judgement_event, ensure_ascii=False) + "\n")
            i += 1

        logger.success("===> contest data package generated successfully.")
    except:
        logger.exception("===> failed to generate contest data package.")
        raise
