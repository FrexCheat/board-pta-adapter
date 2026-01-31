from pydantic import BaseModel


class PTAUser(BaseModel):
    id: str
    nickname: str


class StudentUser(BaseModel):
    studentNumber: str
    name: str
    id: str


class ExamUser(BaseModel):
    examId: str
    userId: str
    userGroupId: str
    studentUserId: str
