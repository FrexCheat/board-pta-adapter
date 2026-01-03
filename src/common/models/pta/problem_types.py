from typing import Any, List

from pydantic import BaseModel


class Problem(BaseModel):
    id: str
    label: str
    score: int
    problemPoolIndex: int
    problemPoolCompositionCount: int
    title: str
    type: str
    indexInProblemPool: int


class ProblemTypes(BaseModel):
    labels: List[Problem]
    problemTypes: List[Any]
