from typing import Any, Dict, List

from pydantic import BaseModel


class PTAUser(BaseModel):
    id: str
    nickname: str


class StudentUser(BaseModel):
    studentNumber: str
    name: str
    id: str


class ExamMember(BaseModel):
    examId: str
    userId: str
    userGroupId: str
    studentUserId: str


class ProblemScoreDetail(BaseModel):
    score: int
    validSubmitCount: int
    acceptTime: int
    submitCountSnapshot: int


class _CommonRanking(BaseModel):
    rank: int
    user: ExamMember
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
    commonRankings: List[_CommonRanking]
    selfRanking: Dict[str, Any]
    labelByProblemSetProblemId: Dict[str, str]
