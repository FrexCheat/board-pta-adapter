from pydantic import BaseModel, ConfigDict


class ExamUser(BaseModel):
    examId: str
    userId: str
    userGroupId: str
    studentUserId: str


class StudentUser(BaseModel):
    studentNumber: str
    name: str
    id: str


class Problem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    label: str
    score: int
    problemPoolIndex: int
    title: str


class ProblemTypes(BaseModel):
    model_config = ConfigDict(extra="allow")

    labels: list[Problem]


class ProblemScoreDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    score: int


class CommonRanking(BaseModel):
    model_config = ConfigDict(extra="allow")

    user: ExamUser
    totalScore: int
    problemScoreByProblemSetProblemId: dict[str, ProblemScoreDetail]


class CommonRankings(BaseModel):
    model_config = ConfigDict(extra="allow")

    total: int
    studentUserById: dict[str, StudentUser]
    commonRankings: list[CommonRanking]


class ProblemSetDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    startAt: str
    endAt: str


class ProblemSet(BaseModel):
    model_config = ConfigDict(extra="allow")

    problemSet: ProblemSetDetail


class Submission(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    userId: str
    problemSetProblemId: str
    submitAt: str
    status: str
    compiler: str


class Submissions(BaseModel):
    model_config = ConfigDict(extra="allow")

    submissions: list[Submission]
    examMemberByUserId: dict[str, ExamUser]
    studentUserById: dict[str, StudentUser]
