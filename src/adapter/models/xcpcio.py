from enum import StrEnum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SubmissionStatus(StrEnum):
    PENDING = "PENDING"
    WAITING = "WAITING"
    PREPARING = "PREPARING"
    COMPILING = "COMPILING"
    RUNNING = "RUNNING"
    JUDGING = "JUDGING"
    FROZEN = "FROZEN"

    ACCEPTED = "ACCEPTED"
    CORRECT = "CORRECT"
    PARTIALLY_CORRECT = "PARTIALLY_CORRECT"

    REJECTED = "REJECTED"
    WRONG_ANSWER = "WRONG_ANSWER"

    NO_OUTPUT = "NO_OUTPUT"

    COMPILATION_ERROR = "COMPILATION_ERROR"
    PRESENTATION_ERROR = "PRESENTATION_ERROR"

    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    OUTPUT_LIMIT_EXCEEDED = "OUTPUT_LIMIT_EXCEEDED"
    IDLENESS_LIMIT_EXCEEDED = "IDLENESS_LIMIT_EXCEEDED"

    HACKED = "HACKED"

    JUDGEMENT_FAILED = "JUDGEMENT_FAILED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    FILE_ERROR = "FILE_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CANCELED = "CANCELED"
    SKIPPED = "SKIPPED"

    SECURITY_VIOLATED = "SECURITY_VIOLATED"
    DENIAL_OF_JUDGEMENT = "DENIAL_OF_JUDGEMENT"

    UNKNOWN = "UNKNOWN"
    UNDEFINED = "UNDEFINED"


class Image(BaseModel):
    url: Optional[str] = None
    mime: Optional[str] = None
    base64: Optional[str] = None
    type: Optional[Literal["png", "svg", "jpg", "jpeg"]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    preset: Optional[Literal["ICPC", "CCPC", "HUNAN_CPC"]] = None


class Organization(BaseModel):
    id: str = None
    name: str = None
    logo: Optional[Image] = None


class Team(BaseModel):
    id: str = None
    name: str = None
    organization_id: str = None
    group: List[str] = Field(default_factory=list)
    coaches: Optional[List[str]] = None
    members: Optional[List[str]] = None
    location: Optional[str] = None


class Submission(BaseModel):
    id: str = None
    team_id: str = None
    problem_id: int = None
    timestamp: int = None
    status: SubmissionStatus = None
    language: Optional[str] = None
