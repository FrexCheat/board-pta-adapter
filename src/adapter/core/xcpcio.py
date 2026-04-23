import hashlib
import time

import pendulum

from adapter.models.config import Config
from adapter.models.xcpcio import Image, Organization, Submission, Team
from adapter.pta_client import PTAClient
from adapter.utils import SheetReader

LANGUAGE_MAPPING = {
    "GCC": "C",
    "CLANG": "C",
    "MODERN_GCC": "C",
    "GXX": "CPP",
    "CLANGXX": "CPP",
    "PYPY3": "PYTHON",
    "PYTHON3": "PYTHON",
    "PYTHON2": "PYTHON",
    "JAVAC": "JAVA",
}

STATUS_MAPPING = {
    "WAIT": "WAITING",
    "WAITING": "WAITING",
    "PENDING": "PENDING",
    "JUDGING": "JUDGING",
    "RUNNING": "RUNNING",
    "ACCEPTED": "ACCEPTED",
    "WRONG_ANSWER": "WRONG_ANSWER",
    "COMPILE_ERROR": "COMPILATION_ERROR",
    "RUNTIME_ERROR": "RUNTIME_ERROR",
    "SEGMENTATION_FAULT": "RUNTIME_ERROR",
    "NON_ZERO_EXIT_CODE": "RUNTIME_ERROR",
    "FLOAT_POINT_EXCEPTION": "RUNTIME_ERROR",
    "TIME_LIMIT_EXCEEDED": "TIME_LIMIT_EXCEEDED",
    "MEMORY_LIMIT_EXCEEDED": "MEMORY_LIMIT_EXCEEDED",
    "OUTPUT_LIMIT_EXCEEDED": "OUTPUT_LIMIT_EXCEEDED",
    "PRESENTATION_ERROR": "PRESENTATION_ERROR",
}


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
        return LANGUAGE_MAPPING.get(language, "UNKNOWN")

    @staticmethod
    def get_status(status: str) -> str:
        return STATUS_MAPPING.get(status, "UNKNOWN")

    @staticmethod
    def _organization_id(school: str) -> str:
        return hashlib.md5(school.encode("utf-8")).hexdigest()[:8]

    def _team_group(self, school: str) -> list[str]:
        official_schools = set(self.config.xcpcio.official_schools)
        if school in official_schools:
            return ["official"]
        return ["unofficial"]

    def get_organizations(self) -> list[Organization]:
        organizations: list[Organization] = []

        source = self.sheet.load()
        df = source.iloc[:, [4]].copy()
        df.columns = ["school"]
        df["school"] = df["school"].astype(str).str.strip()
        df_unique = df.drop_duplicates(subset=["school"], keep="first")
        school_set = df_unique["school"].tolist()
        for school in school_set:
            organization_id = self._organization_id(school)
            organization_kwargs = {
                "id": organization_id,
                "name": school,
            }
            organization_kwargs["logo"] = Image(
                url=f"{self.config.xcpcio.contest_path}/assets/logos/{organization_id}.png"
            )
            organization = Organization(**organization_kwargs)
            organizations.append(organization)

        return organizations

    def get_teams(self) -> list[Team]:
        teams: list[Team] = []

        source = self.sheet.load()
        df = source.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]].copy()
        df.columns = ["room", "loc_num", "id", "name", "school", "member_1", "member_2", "member_3"]
        df["room"] = df["room"].astype(str).str.strip()
        df["loc_num"] = df["loc_num"].astype(str).str.strip()
        df["id"] = df["id"].astype(str).str.strip()
        df["name"] = df["name"].astype(str).str.strip()
        df["school"] = df["school"].astype(str).str.strip()
        df["member_1"] = df["member_1"].astype(str).str.strip()
        df["member_2"] = df["member_2"].astype(str).str.strip()
        df["member_3"] = df["member_3"].astype(str).str.strip()
        data = df.to_dict(orient="records")
        for item in data:
            members = [item["member_1"], item["member_2"], item["member_3"]]
            team_kwargs = {
                "id": item["id"],
                "name": item["name"],
                "organization_id": self._organization_id(item["school"]),
                "group": self._team_group(item["school"]),
            }
            team_kwargs["members"] = [member for member in members if not SheetReader.is_empty(member)]
            team_kwargs["location"] = f"{item['room']}-{item['loc_num']}"
            team = Team(**team_kwargs)
            teams.append(team)

        return teams

    def get_submissions(self) -> tuple[list[Submission], list[Submission]]:
        submissions: list[Submission] = []
        submissions_unfrozen: list[Submission] = []

        contest_info = self.pta_client.fetch_problem_set()
        problem_info = self.pta_client.fetch_problem_types()
        submissions_info = self.pta_client.fetch_submissions(before=None, limit=200)

        start_time = pendulum.parse(contest_info.problemSet.startAt)
        end_time = pendulum.parse(contest_info.problemSet.endAt)
        frozen_time = end_time.subtract(seconds=self.config.xcpcio.config.frozen_time)
        problem_mapping = {problem.id: problem.problemPoolIndex - 1 for problem in problem_info.labels}

        while submissions_info.submissions:
            exam_member_by_user_id = submissions_info.examMemberByUserId
            student_user_by_id = submissions_info.studentUserById
            for submission in submissions_info.submissions:
                submit_at = pendulum.parse(submission.submitAt)
                timestamp = int((submit_at - start_time).total_seconds() * 1000)
                status = self.get_status(submission.status)
                team_id = student_user_by_id[exam_member_by_user_id[submission.userId].studentUserId].studentNumber
                problem_id = problem_mapping[submission.problemSetProblemId]
                language = self.get_languages(submission.compiler)

                submissions.append(
                    Submission(
                        id=submission.id,
                        team_id=team_id,
                        problem_id=problem_id,
                        timestamp=timestamp,
                        status="FROZEN" if submit_at > frozen_time else status,
                        language=language,
                    )
                )
                submissions_unfrozen.append(
                    Submission(
                        id=submission.id,
                        team_id=team_id,
                        problem_id=problem_id,
                        timestamp=timestamp,
                        status=status,
                        language=language,
                    )
                )

            time.sleep(1)
            submissions_info = self.pta_client.fetch_submissions(before=submissions_info.submissions[-1].id, limit=200)

        return submissions, submissions_unfrozen
