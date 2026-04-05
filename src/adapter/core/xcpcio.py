import hashlib
import time
from typing import List

import pendulum

from adapter.models.config import Config
from adapter.models.xcpcio import Organization, Submission, SubmissionStatus, Team
from common.pta.client import PTAClient
from common.utils.excel import SheetReader

LANGUAGE_MAPPING = {
    "GCC": "C",
    "CLANG": "C",
    "MODERN_GCC": "C",
    "GXX": "C++",
    "CLANGXX": "C++",
    "PYPY3": "Python",
    "PYTHON3": "Python",
    "PYTHON2": "Python",
    "JAVAC": "Java",
}

STATUS_MAPPING = {
    "WAIT": SubmissionStatus.WAITING,
    "WAITING": SubmissionStatus.WAITING,
    "PENDING": SubmissionStatus.PENDING,
    "JUDGING": SubmissionStatus.JUDGING,
    "RUNNING": SubmissionStatus.RUNNING,
    "ACCEPTED": SubmissionStatus.ACCEPTED,
    "WRONG_ANSWER": SubmissionStatus.WRONG_ANSWER,
    "COMPILE_ERROR": SubmissionStatus.COMPILATION_ERROR,
    "RUNTIME_ERROR": SubmissionStatus.RUNTIME_ERROR,
    "SEGMENTATION_FAULT": SubmissionStatus.RUNTIME_ERROR,
    "NON_ZERO_EXIT_CODE": SubmissionStatus.RUNTIME_ERROR,
    "FLOAT_POINT_EXCEPTION": SubmissionStatus.RUNTIME_ERROR,
    "TIME_LIMIT_EXCEEDED": SubmissionStatus.TIME_LIMIT_EXCEEDED,
    "MEMORY_LIMIT_EXCEEDED": SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
    "OUTPUT_LIMIT_EXCEEDED": SubmissionStatus.OUTPUT_LIMIT_EXCEEDED,
    "PRESENTATION_ERROR": SubmissionStatus.PRESENTATION_ERROR,
    "SYSTEM_ERROR": SubmissionStatus.SYSTEM_ERROR,
}

OFFICIAL_SCHOOLS = {"郑州轻工业大学"}


class XCPCIOAdapter:
    def __init__(self, config: Config):
        self.config = config
        self.sheet = SheetReader(config.xcpcio.excel_path, config.xcpcio.sheet_name)
        self.pta_client = PTAClient(
            pta_session=config.pta.pta_session,
            problem_set_id=config.pta.problem_set_id,
        )

    @staticmethod
    def get_languages(language: str) -> str:
        return LANGUAGE_MAPPING.get(language, language)

    @staticmethod
    def get_status(status: str) -> SubmissionStatus:
        return STATUS_MAPPING.get(status, SubmissionStatus.UNKNOWN)

    def get_organizations(self, enable_logo: bool = True) -> List[Organization]:
        organizations: List[Organization] = []

        source = self.sheet.load()
        df = source.iloc[:, [4]].copy()
        df.columns = ["school"]
        df["school"] = df["school"].astype(str).str.strip()
        df_unique = df.drop_duplicates(subset=["school"], keep="first")
        school_set = df_unique["school"].tolist()
        for item in school_set:
            _hash = hashlib.md5(item.encode("utf-8")).hexdigest()[:8]
            _organizations = dict()
            _organizations["id"] = _hash
            _organizations["name"] = item

            if enable_logo:
                _organizations["logo"] = dict()
                _organizations["logo"]["url"] = f"{self.config.xcpcio.contest_path}/assets/logos/{_hash}.png"

            organization = Organization.model_validate(_organizations)
            organizations.append(organization)
        return organizations

    def get_teams(self, single: bool = False) -> List[Team]:
        teams: List[Team] = []

        source = self.sheet.load()
        df = source.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]].copy()
        df.columns = ["room", "loc_num", "id", "name", "school", "member_1", "member_2", "member_3"]
        df["id"] = df["id"].astype(str).str.strip()
        df["name"] = df["name"].astype(str)
        df["school"] = df["school"].astype(str).str.strip()
        df["loc_num"] = df["loc_num"].astype(str).str.strip()
        df["member_1"] = df["member_1"].astype(str).str.strip()
        df["member_2"] = df["member_2"].astype(str).str.strip()
        df["member_3"] = df["member_3"].astype(str).str.strip()
        data = df.to_dict(orient="records")
        for item in data:
            _hash = hashlib.md5(item["school"].encode("utf-8")).hexdigest()[:8]
            _teams = dict()
            _teams["id"] = item["id"]
            _teams["name"] = item["name"]
            _teams["organization_id"] = _hash

            _teams["group"] = []
            if item["school"] in OFFICIAL_SCHOOLS:
                _teams["group"].append("official")
            else:
                _teams["group"].append("unofficial")

            _members = [item["member_1"], item["member_2"], item["member_3"]]
            if single and not SheetReader.is_empty(_members[0]):
                _teams["members"] = [_members[0]]
            else:
                _teams["members"] = [m for m in _members if not SheetReader.is_empty(m)]

            _teams["location"] = item["room"] + "-" + item["loc_num"]
            team = Team.model_validate(_teams)
            teams.append(team)
        return teams

    def get_submissions(self, is_frozen: bool = True) -> List[Submission]:
        submissions: List[Submission] = []

        _contest_info = self.pta_client.fetch_problem_set()
        _problem_info = self.pta_client.fetch_problem_types()
        _submissions_info = self.pta_client.fetch_submissions(before=None, limit=200)

        _start_time = pendulum.parse(_contest_info.problemSet.startAt)
        _end_time = pendulum.parse(_contest_info.problemSet.endAt)
        _frozen_time = _end_time.subtract(seconds=self.config.xcpcio.frozen_diff)
        _problem_mapping = {p.id: p.problemPoolIndex - 1 for p in _problem_info.labels}

        while _submissions_info.submissions:
            _examMemberByUserId = _submissions_info.examMemberByUserId
            _studentUserById = _submissions_info.studentUserById
            for s in _submissions_info.submissions:
                _submission = dict()
                _submission["id"] = s.id
                _submission["team_id"] = _studentUserById[_examMemberByUserId[s.userId].studentUserId].studentNumber
                _submission["problem_id"] = _problem_mapping.get(s.problemSetProblemId)

                _submit_at = pendulum.parse(s.submitAt)
                _timestamp = (_submit_at - _start_time).total_seconds() * 1000
                _submission["timestamp"] = _timestamp

                if is_frozen and _submit_at > _frozen_time:
                    _submission["status"] = SubmissionStatus.FROZEN
                else:
                    _submission["status"] = self.get_status(s.status)

                _submission["language"] = self.get_languages(s.compiler)
                submission = Submission.model_validate(_submission)
                submissions.append(submission)

            time.sleep(1)
            _submissions_info = self.pta_client.fetch_submissions(before=_submissions_info.submissions[-1].id, limit=200)

        return submissions
