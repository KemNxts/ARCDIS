from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.agent import AgentRegister, AgentResponse, AgentHeartbeatResponse
from app.services.agent_service import register_agent, update_agent_heartbeat
from app.utils.dependencies import get_current_user
from app.database import get_agent_collection

router = APIRouter()

@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register(agent_in: AgentRegister, current_user: dict = Depends(get_current_user)):
    return await register_agent(str(current_user["id"]), agent_in)

@router.get("", response_model=List[AgentResponse])
async def list_agents(current_user: dict = Depends(get_current_user)):
    agents_col = get_agent_collection()
    cursor = agents_col.find({"user_id": str(current_user["id"])})
    agents = await cursor.to_list(length=100)
    for agent in agents:
        agent["id"] = str(agent.pop("_id"))
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    agents_col = get_agent_collection()
    agent = await agents_col.find_one({"agent_id": agent_id, "user_id": str(current_user["id"])})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent["id"] = str(agent.pop("_id"))
    return agent

@router.patch("/{agent_id}/heartbeat", response_model=AgentHeartbeatResponse)
async def heartbeat(agent_id: str, current_user: dict = Depends(get_current_user)):
    return await update_agent_heartbeat(str(current_user["id"]), agent_id)
