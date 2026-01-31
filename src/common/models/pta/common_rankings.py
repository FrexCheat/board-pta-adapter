from typing import Any, Dict, List

from pydantic import BaseModel

from .base import ExamUser, PTAUser, StudentUser


class ProblemScoreDetail(BaseModel):
    score: int
    validSubmitCount: int
    acceptTime: int
    submitCountSnapshot: int


class CommonRanking(BaseModel):
    rank: int
    user: ExamUser
    examId: str
    totalScore: int
    typeScores: Dict[str, int]
    solvingTime: int
    problemScoreByProblemSetProblemId: Dict[str, ProblemScoreDetail]
    startAt: str


class CommonRankings(BaseModel):
    total: int
    userById: Dict[str, PTAUser]
    studentUserById: Dict[str, StudentUser]
    labels: List[str]
    commonRankings: List[CommonRanking]
    selfRanking: Dict[str, Any]
    labelByProblemSetProblemId: Dict[str, str]
