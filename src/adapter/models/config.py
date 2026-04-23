from pydantic import BaseModel, Field


class PTAConfig(BaseModel):
    pta_session: str
    problem_set_id: str


class GPLTConfig(BaseModel):
    output_dir: str
    excel_path: str
    sheet_name: str
    standard_1: int
    standard_2: int


class XCPCIOContestConfig(BaseModel):
    contest_name: str
    start_time: int
    end_time: int
    penalty: int
    frozen_time: int
    problem_id: list[str]
    balloon_color: list[dict]
    options: dict
    organizations: dict
    logo: dict
    status_time_display: dict
    group: dict
    medal: dict


class XCPCIOConfig(BaseModel):
    output_dir: str
    excel_path: str
    sheet_name: str
    contest_path: str
    unfrozen_path: str
    official_schools: list[str] = Field(default_factory=list)
    config: XCPCIOContestConfig


class Config(BaseModel):
    sync_interval: int
    pta: PTAConfig
    gplt: GPLTConfig
    xcpcio: XCPCIOConfig
