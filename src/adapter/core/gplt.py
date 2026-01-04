import time
from typing import List

from adapter.models.config import Config
from adapter.models.gplt import Contest, Ranking, Student, Team
from common.pta.client import PTAClient
from common.utils.excel import SheetReader


class GPLTAdapter:
    def __init__(self, config: Config):
        self.config = config
        self.sheet = SheetReader(config.gplt.excel_path, config.gplt.sheet_name)
        self.pta_client = PTAClient(
            pta_session=config.pta.pta_session,
            problem_set_id=config.pta.problem_set_id,
        )

    def get_contest(self) -> Contest:
        problem_set = self.pta_client.fetch_problem_set()
        problem_types = self.pta_client.fetch_problem_types()
        problem_list = problem_types.labels
        contest = Contest(
            title=problem_set.problemSet.name,
            standard_1=self.config.gplt.standard_1,
            standard_2=self.config.gplt.standard_2,
            problems=[{"id": p.id, "label": p.label, "score": p.score} for p in problem_list],
        )
        return contest

    def get_students(self) -> List[Student]:
        students: List[Student] = []

        source = self.sheet.load()
        df = source.iloc[:, [0, 1, 2, 3, 5, 6]].copy()
        df.columns = ["id", "team_id", "name", "school", "college", "class"]
        df["id"] = df["id"].astype(str).str.strip()
        df["team_id"] = df["team_id"].astype(str).str.strip()
        df["name"] = df["name"].astype(str).str.strip()
        data = df.to_dict(orient="records")
        for item in data:
            student = Student.model_validate(item)
            students.append(student)
        return students

    def get_teams(self) -> List[Team]:
        teams: List[Team] = []

        source = self.sheet.load()
        df = source.iloc[:, [1, 4, 3, 5, 6]].copy()
        df.columns = ["id", "name", "school", "college", "class"]
        df["id"] = df["id"].astype(str).str.strip()
        data = df.to_dict(orient="records")
        for item in data:
            team = Team.model_validate(item)
            teams.append(team)
        return teams

    def get_rankings(self) -> List[Ranking]:
        rankings: List[Ranking] = []

        first_page = self.pta_client.fetch_common_rankings(0, 100)
        total_count = first_page.total
        page_count = total_count // 100 + (1 if total_count % 100 else 0)

        for page in range(page_count):
            common_rankings = self.pta_client.fetch_common_rankings(page, 100)
            for idx, item in enumerate(common_rankings.commonRankings):
                ranking = Ranking(
                    id=common_rankings.studentUserById[item.user.studentUserId].studentNumber,
                    rank=idx + page * 100 + 1,
                    score=item.totalScore,
                    problems_score={k: v.score for k, v in item.problemScoreByProblemSetProblemId.items()},
                )
                rankings.append(ranking)
            time.sleep(1)
        return rankings
