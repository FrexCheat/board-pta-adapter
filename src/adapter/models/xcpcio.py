from typing import List, Literal, Optional

from pydantic import BaseModel, Field


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
    status: str = None
    language: Optional[str] = None
