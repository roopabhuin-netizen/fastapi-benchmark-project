from pydantic import BaseModel
from typing import Dict


class SystemConfig(BaseModel):
    cpu: str
    cores: int
    ram_gb: int
    kernel: str


class ExecutionCreate(BaseModel):
    benchmark_name: str
    git_commit: str 
    system_config: SystemConfig
    metrics: Dict[str, float]
