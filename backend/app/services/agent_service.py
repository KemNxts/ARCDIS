from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.database import get_agent_collection
from app.schemas.agent import AgentRegister
from app.models.agent import AgentModel

async def register_agent(user_id: str, agent_in: AgentRegister) -> dict:
    agents_col = get_agent_collection()
    
    existing_agent = await agents_col.find_one({"agent_id": agent_in.agent_id})
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this ID already exists"
        )
        
    new_agent = AgentModel(
        agent_id=agent_in.agent_id,
        user_id=user_id,
        hostname=agent_in.hostname,
        os_info=agent_in.os_info,
        version=agent_in.version,
    )
    
    result = await agents_col.insert_one(new_agent.model_dump(by_alias=True, exclude_none=True))
    created_agent = await agents_col.find_one({"_id": result.inserted_id})
    created_agent["id"] = str(created_agent.pop("_id"))
    return created_agent

async def update_agent_heartbeat(user_id: str, agent_id: str) -> dict:
    agents_col = get_agent_collection()
    now = datetime.now(timezone.utc)
    
    result = await agents_col.update_one(
        {"agent_id": agent_id, "user_id": user_id},
        {"$set": {"last_seen": now, "status": "online"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
        
    return {"status": "online", "last_seen": now}
