from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

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
    risk_level: Optional[RiskLevel] = None
    text: str

class RiskLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class EnvironmentState(BaseModel):
    case_id: str
    task_id: str
    ground_truth: str
    risk_level: Optional[RiskLevel] = None
    is_done: bool
    total_reward: float
