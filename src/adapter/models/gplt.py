from pydantic import BaseModel, Field


class Problem(BaseModel):
    id: str
    label: str
    score: int


class Contest(BaseModel):
    title: str
    standard_1: int
    standard_2: int
    problems: list[Problem]


class Student(BaseModel):
    id: str
    team_id: str
    name: str
    school: str
    college: str | None = None
    class_: str | None = Field(..., alias="class")


class Team(BaseModel):
    id: str
    name: str
    school: str
    college: str | None = None
    class_: str | None = Field(..., alias="class")


class Ranking(BaseModel):
    id: str
    rank: int
    score: int
    problems_score: dict[str, int]
