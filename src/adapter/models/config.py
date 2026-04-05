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


class XCPCIOConfig(BaseModel):
    output_dir: str
    excel_path: str
    sheet_name: str
    contest_path: str
    config: dict


class Config(BaseModel):
    sync_interval: int
    pta: PTAConfig
    gplt: GPLTConfig
    xcpcio: XCPCIOConfig
