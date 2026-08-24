from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentRegister(BaseModel):
    agent_id: str
    hostname: str
    os_info: str
    version: str

class AgentResponse(BaseModel):
    id: str
    agent_id: str
    user_id: str
    hostname: str
    os_info: str
    status: str
    last_seen: datetime
    created_at: datetime
    version: str

    class Config:
        from_attributes = True

class AgentHeartbeatResponse(BaseModel):
    status: str
    last_seen: datetime
