from pydantic import BaseModel, StrictStr,StrictFloat
from typing import Dict


class MetricRule(BaseModel):
    unit: StrictStr
    better: StrictStr
    tolerance_percent: StrictFloat


class BenchmarkCreate(BaseModel):
    name: StrictStr
    display_name: StrictStr
    category: StrictStr
    description: StrictStr 
    created_by: StrictStr
    metric_rules: Dict[StrictStr, MetricRule]
