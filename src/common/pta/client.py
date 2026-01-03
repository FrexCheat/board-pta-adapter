from typing import Any, Dict

import requests

from common.models.pta import CommonRankings, ProblemSet, ProblemTypes, Submissions


class PTAClient:
    API_ROOT = "https://pintia.cn/api"

    def __init__(self, pta_session: str, problem_set_id: str) -> None:
        self.pta_session = pta_session
        self.problem_set_id = problem_set_id
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        self.session.cookies.update({"PTASession": self.pta_session})
        self.session.headers.update(
            {
                "Content-Type": "application/json;charset=UTF-8",
                "Accept": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            }
        )
        bootstrap = f"{self.API_ROOT}/problem-sets/{self.problem_set_id}"
        response = self.session.get(bootstrap)
        response.raise_for_status()
        self.session.cookies.update(response.cookies)

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = f"{self.API_ROOT}{path}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        self.session.cookies.update(response.cookies)
        return response.json()

    def fetch_problem_set(self) -> ProblemSet:
        payload = self._get(f"/problem-sets/{self.problem_set_id}")
        return ProblemSet.model_validate(payload)

    def fetch_problem_types(self) -> ProblemTypes:
        payload = self._get(f"/problem-sets/{self.problem_set_id}/problem-types")
        return ProblemTypes.model_validate(payload)

    def fetch_common_rankings(self, page: int, limit: int) -> CommonRankings:
        params = {"page": page, "limit": limit}
        payload = self._get(f"/problem-sets/{self.problem_set_id}/common-rankings", params=params)
        return CommonRankings.model_validate(payload)

    def fetch_submissions(self, before: str, limit: int) -> Submissions:
        params = {"before": before, "limit": limit, "filter": "%7B%7D"}
        payload = self._get(f"/problem-sets/{self.problem_set_id}/submissions", params=params)
        return Submissions.model_validate(payload)
