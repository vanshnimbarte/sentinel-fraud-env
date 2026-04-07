from pydantic import BaseModel
from typing import List

class InvestigationAction(BaseModel):
    command: str

class EvidenceItem(BaseModel):
    query: str
    result: str
    informativeness: float

class FraudObservation(BaseModel):
    alert: str
    evidence: List[EvidenceItem]
    budget_remaining: int
    step_count: int
    text: str

class EnvironmentState(BaseModel):
    case_id: str
    task_id: str
    ground_truth: str
    is_done: bool
    total_reward: float
