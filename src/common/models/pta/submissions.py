from typing import Dict, List

from pydantic import BaseModel

from .common_rankings import ExamMember, PTAUser, StudentUser
from .problem_types import Problem


class Submission(BaseModel):
    id: str
    userId: str
    problemType: str
    problemSetProblemId: str
    submitAt: str
    status: str
    score: float
    compiler: str
    time: float
    memory: int
    previewSubmission: bool
    judgeAt: str


class Submissions(BaseModel):
    submissions: List[Submission]
    hasAfter: bool
    hasBefore: bool
    total: int
    problemSetProblemById: Dict[str, Problem]
    examMemberByUserId: Dict[str, ExamMember]
    showDetailBySubmissionId: Dict[str, bool]
    userById: Dict[str, PTAUser]
    studentUserById: Dict[str, StudentUser]
