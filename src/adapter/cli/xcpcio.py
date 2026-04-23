import json
import shutil
import time
from itertools import count
from pathlib import Path

from loguru import logger

from adapter.config import load_config
from adapter.core.xcpcio import XCPCIOAdapter
from adapter.pta_client import PTAClientError
from adapter.utils import calc_ms_time_diff, format_ms_to_time

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

LANGUAGES_ID = ["C", "CPP", "PYTHON", "JAVA"]


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _build_runtime():
    config = load_config()
    adapter = XCPCIOAdapter(config)
    output_dir = Path(config.xcpcio.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return config, adapter, output_dir


def _write_event(
    output_dir: Path, token_counter, event_type: str, data: dict, event_id: str | int | None = None
) -> None:
    event = {"type": event_type, "data": data, "token": f"t{next(token_counter)}"}
    if event_id is not None:
        event["id"] = event_id
    feed = output_dir / "cdp/event-feed.ndjson"
    feed.parent.mkdir(parents=True, exist_ok=True)
    with feed.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _write_to_both(output_dir: Path, unfrozen_path: str, filename: str, data) -> None:
    _write_json(output_dir / filename, data)
    _write_json(output_dir / unfrozen_path / filename, data)


def generate() -> None:
    logger.info("===> starting to generate static data...")
    config, adapter, output_dir = _build_runtime()
    unfrozen = config.xcpcio.unfrozen_path

    logger.info("generating config.json...")
    _write_to_both(output_dir, unfrozen, "config.json", config.xcpcio.config.model_dump())

    logger.info("generating organizations.json...")
    organizations = adapter.get_organizations()
    organizations_payload = [o.model_dump(by_alias=True, exclude_unset=True) for o in organizations]
    _write_to_both(output_dir, unfrozen, "organizations.json", organizations_payload)

    logger.info("generating team.json...")
    teams = adapter.get_teams()
    teams_payload = [t.model_dump(by_alias=True, exclude_unset=True) for t in teams]
    _write_to_both(output_dir, unfrozen, "team.json", teams_payload)

    logger.success("===> static data generated successfully.")


def synchronize() -> None:
    logger.info("===> starting to synchronize submissions data...")
    config, adapter, output_dir = _build_runtime()
    unfrozen = config.xcpcio.unfrozen_path
    while True:
        try:
            logger.info("generating run.json...")
            submissions, submissions_unfrozen = adapter.get_submissions()
            _write_json(output_dir / "run.json", [s.model_dump() for s in submissions])
            _write_json(output_dir / unfrozen / "run.json", [s.model_dump() for s in submissions_unfrozen])
            logger.success("===> submissions data synchronized successfully.")
        except PTAClientError:
            logger.exception("PTA API unreachable, will retry next cycle.")
        except Exception:
            logger.exception("unexpected error during sync, crashing.")
            raise

        logger.info("sleep for {} seconds before next synchronization...", config.sync_interval)
        time.sleep(config.sync_interval)


def cdp() -> None:
    logger.info("===> starting to generate contest data package...")
    config, adapter, output_dir = _build_runtime()

    cdp_dir = output_dir / "cdp"
    shutil.rmtree(cdp_dir, ignore_errors=True)
    (cdp_dir / "organizations").mkdir(parents=True, exist_ok=True)
    token_counter = count()

    state_data = {
        "started": format_ms_to_time(config.xcpcio.config.start_time),
        "ended": format_ms_to_time(config.xcpcio.config.end_time),
        "frozen": format_ms_to_time(config.xcpcio.config.end_time - (config.xcpcio.config.frozen_time * 1000)),
        "thawed": None,
        "finalized": format_ms_to_time(config.xcpcio.config.end_time + (120 * 1000)),
        "end_of_updates": format_ms_to_time(config.xcpcio.config.end_time + (150 * 1000)),
    }
    _write_event(output_dir, token_counter, "state", state_data)

    contest_data = {
        "id": config.pta.problem_set_id,
        "name": config.xcpcio.config.contest_name,
        "formal_name": config.xcpcio.config.contest_name,
        "start_time": format_ms_to_time(config.xcpcio.config.start_time),
        "duration": calc_ms_time_diff(config.xcpcio.config.start_time, config.xcpcio.config.end_time),
        "scoreboard_type": "pass-fail",
        "scoreboard_freeze_duration": calc_ms_time_diff(0, config.xcpcio.config.frozen_time * 1000),
        "penalty_time": int(config.xcpcio.config.penalty / 60),
    }
    _write_event(output_dir, token_counter, "contest", contest_data, config.pta.problem_set_id)

    for name, judgement_id in JUDGEMENT_ID_MAPPING.items():
        _write_event(
            output_dir,
            token_counter,
            "judgement-types",
            {
                "id": judgement_id,
                "name": name,
                "penalty": judgement_id not in {"AC", "CE"},
                "solved": judgement_id == "AC",
            },
            judgement_id,
        )

    for language_id in LANGUAGES_ID:
        _write_event(
            output_dir,
            token_counter,
            "languages",
            {"id": language_id, "name": language_id, "entry_point_required": False},
            language_id,
        )

    problems = adapter.pta_client.fetch_problem_types()
    for problem in problems.labels:
        _write_event(
            output_dir,
            token_counter,
            "problems",
            {
                "id": problem.problemPoolIndex - 1,
                "name": problem.title,
                "label": problem.label,
                "ordinal": problem.problemPoolIndex,
                "rgb": config.xcpcio.config.balloon_color[problem.problemPoolIndex - 1],
            },
            problem.problemPoolIndex - 1,
        )

    for group_id, name in config.xcpcio.config.group.items():
        _write_event(output_dir, token_counter, "groups", {"id": group_id, "name": name}, group_id)

    organizations = adapter.get_organizations()
    for organization in organizations:
        _write_event(
            output_dir,
            token_counter,
            "organizations",
            {"id": organization.id, "name": organization.name, "formal_name": organization.name},
            organization.id,
        )
        org_dir = cdp_dir / "organizations" / organization.id
        org_dir.mkdir(parents=True, exist_ok=True)
        logo_src = output_dir / "logos" / f"{organization.id}.png"
        shutil.copy2(logo_src, org_dir / "logo.png")

    teams = adapter.get_teams()
    for team in teams:
        _write_event(
            output_dir,
            token_counter,
            "teams",
            {
                "id": team.id,
                "label": team.id,
                "name": team.name,
                "display_name": team.name,
                "organization_id": team.organization_id,
                "group_ids": team.group,
            },
            team.id,
        )

    _, submissions = adapter.get_submissions()
    for submission in submissions:
        if submission.language not in LANGUAGES_ID:
            raise ValueError(f"Unknown language {submission.language} for submission {submission.id}!")
        if submission.status not in JUDGEMENT_ID_MAPPING:
            raise ValueError(f"Unknown status {submission.status} for submission {submission.id}!")

        _write_event(
            output_dir,
            token_counter,
            "submissions",
            {
                "id": submission.id,
                "team_id": submission.team_id,
                "problem_id": submission.problem_id,
                "language_id": submission.language,
                "time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "contest_time": calc_ms_time_diff(0, submission.timestamp),
            },
            submission.id,
        )
        _write_event(
            output_dir,
            token_counter,
            "judgements",
            {
                "id": f"j-{submission.id}",
                "submission_id": submission.id,
                "judgement_type_id": JUDGEMENT_ID_MAPPING[submission.status],
                "start_time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "start_contest_time": calc_ms_time_diff(0, submission.timestamp),
                "end_time": format_ms_to_time(config.xcpcio.config.start_time + submission.timestamp),
                "end_contest_time": calc_ms_time_diff(0, submission.timestamp),
            },
            f"j-{submission.id}",
        )

    logger.success("===> contest data package generated successfully.")
