import time
from typing import Any, Dict

import requests
from loguru import logger

from common.models.pta import CommonRankings, ProblemSet, ProblemTypes, Submissions


class PTAClientError(RuntimeError):
    pass


class PTAClient:
    API_ROOT = "https://pintia.cn/api"
    REQUEST_TIMEOUT_SECONDS = 15
    MAX_RETRIES = 3

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
        self._request(f"/problem-sets/{self.problem_set_id}")

    def _request(self, path: str, params: Dict[str, Any] | None = None) -> requests.Response:
        url = f"{self.API_ROOT}{path}"
        last_error: requests.RequestException | None = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                self.session.cookies.update(response.cookies)
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt == self.MAX_RETRIES:
                    break

                logger.warning(
                    "PTA request failed on attempt {attempt}/{max_retries}: {path}. Retrying in {sleep}s.",
                    attempt=attempt,
                    max_retries=self.MAX_RETRIES,
                    path=path,
                    sleep=2,
                )
                time.sleep(2)

        raise PTAClientError(f"Failed to fetch PTA API after {self.MAX_RETRIES} attempts: {url}") from last_error

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self._request(path, params=params).json()

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

    def fetch_submissions(self, before: str | None, limit: int) -> Submissions:
        params = {"before": before, "limit": limit, "filter": "{}"}
        payload = self._get(f"/problem-sets/{self.problem_set_id}/submissions", params=params)
        return Submissions.model_validate(payload)
