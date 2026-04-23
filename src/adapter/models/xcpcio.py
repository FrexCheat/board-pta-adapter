from typing import Literal

from pydantic import BaseModel, Field


class Image(BaseModel):
    url: str | None = None
    mime: str | None = None
    base64: str | None = None
    type: Literal["png", "svg", "jpg", "jpeg"] | None = None
    width: int | None = None
    height: int | None = None
    preset: Literal["ICPC", "CCPC", "HUNAN_CPC"] | None = None


class Organization(BaseModel):
    id: str
    name: str
    logo: Image | None = None


class Team(BaseModel):
    id: str
    name: str
    organization_id: str
    group: list[str] = Field(default_factory=list)
    coaches: list[str] | None = None
    members: list[str] = Field(default_factory=list)
    location: str | None = None


class Submission(BaseModel):
    id: str
    team_id: str
    problem_id: int
    timestamp: int
    status: str
    language: str
