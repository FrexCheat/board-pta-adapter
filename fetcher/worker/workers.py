import json
import time

import requests


def get_session(PTASession: str, ProblemSetId: str):
    session = requests.Session()

    cookies = {"PTASession": PTASession}

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    }

    session.cookies.update(cookies)
    session.headers.update(headers)

    response = session.get(f"https://pintia.cn/api/problem-sets/{ProblemSetId}")
    session.cookies.update(response.cookies)

    return session


def fetch_problem_set_info(PTASession: str, ProblemSetId: str):
    url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}"
    session = get_session(PTASession, ProblemSetId)
    response = session.get(url)
    session.cookies.update(response.cookies)

    data = json.loads(response.text)
    return data["problemSet"]


def fetch_problem_list(PTASession: str, ProblemSetId: str):
    result = []

    url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}/problem-types?"
    session = get_session(PTASession, ProblemSetId)
    response = session.get(url)
    session.cookies.update(response.cookies)

    data = json.loads(response.text)
    problems = list(data["labels"])

    for problem in problems:
        _result = {}
        _result["id"] = str(problem["id"])
        _result["label"] = str(problem["label"])
        _result["score"] = int(problem["score"])
        result.append(_result)

    return result


def fetch_common_ranking(PTASession: str, ProblemSetId: str):
    result = []

    url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}/common-rankings?page=0&limit=100"
    session = get_session(PTASession, ProblemSetId)
    response = session.get(url)
    session.cookies.update(response.cookies)

    data = json.loads(response.text)
    totalCount = int(data["total"])
    if totalCount % 100 == 0:
        page_count = int(totalCount / 100)
    else:
        page_count = int(totalCount / 100) + 1

    for i in range(page_count):
        url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}/common-rankings?page={i}&limit=100"
        response = session.get(url)
        session.cookies.update(response.cookies)

        data = json.loads(response.text)
        commonRanking = data["commonRankings"]
        studentUserById = data["studentUserById"]

        for idx, item in enumerate(commonRanking):
            _result = {}
            studentUserId = str(item["user"]["studentUserId"])
            problemScoreByProblemSetProblemId = dict(item["problemScoreByProblemSetProblemId"])
            _result["id"] = str(studentUserById[studentUserId]["studentNumber"])
            _result["rank"] = idx + i * 100 + 1
            _result["score"] = int(item["totalScore"])
            _result["problems_score"] = {str(k): int(v["score"]) for k, v in problemScoreByProblemSetProblemId.items()}
            result.append(_result)

        time.sleep(1)

    return result
