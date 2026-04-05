from pydantic import BaseModel


class PTAConfig(BaseModel):
    pta_session: str
    problem_set_id: str


class GPLTConfig(BaseModel):
    output_dir: str
    excel_path: str
    sheet_name: str
    standard_1: int
    standard_2: int


class XCPCIOConfigJsonConfig(BaseModel):
    contest_name: str
    start_time: int
    end_time: int
    penalty: int
    frozen_time: int
    problem_id: list[str]
    balloon_color: list[str]
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
    config: XCPCIOConfigJsonConfig


class CDPConfig(BaseModel):
    output_dir: str


class Config(BaseModel):
    sync_interval: int
    pta: PTAConfig
    gplt: GPLTConfig
    xcpcio: XCPCIOConfig
    cdp: CDPConfig
