from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AttackReport(BaseModel):
    attack_id: str
    agent_id: str
    technique: str
    title: str
    description: str
    features: Dict[str, Any]
    action_taken: str
    severity: str
    local_anomaly_score: float = 0.0
    raw_summary: Optional[str] = None

class AttackResponse(BaseModel):
    id: str
    attack_id: str
    agent_id: str
    user_id: str
    technique: str
    title: str
    description: str
    features: Dict[str, Any]
    action_taken: str
    severity: str
    local_anomaly_score: float = 0.0
    timestamp: datetime
    raw_summary: Optional[str] = None

    class Config:
        from_attributes = True
