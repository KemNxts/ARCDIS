from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from app.schemas.attack import AttackReport, AttackResponse
from app.models.attack import AttackModel
from app.utils.dependencies import get_current_user, get_agent_identity
from app.database import get_attack_collection, get_agent_collection

router = APIRouter()

@router.post("", response_model=AttackResponse, status_code=201)
async def report_attack(attack_in: AttackReport, current_user: dict = Depends(get_agent_identity)):
    # Verify agent belongs to user
    agents_col = get_agent_collection()
    agent = await agents_col.find_one({"agent_id": attack_in.agent_id, "user_id": str(current_user["id"])})
    if not agent:
        raise HTTPException(status_code=400, detail="Invalid agent ID for this user")
        
    attacks_col = get_attack_collection()
    new_attack = AttackModel(
        **attack_in.model_dump(),
        user_id=str(current_user["id"])
    )
    result = await attacks_col.insert_one(new_attack.model_dump(by_alias=True, exclude_none=True))
    created_attack = await attacks_col.find_one({"_id": result.inserted_id})
    created_attack["id"] = str(created_attack.pop("_id"))
    return created_attack

@router.get("", response_model=List[AttackResponse])
async def list_attacks(
    agent_id: Optional[str] = None,
    technique: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    attacks_col = get_attack_collection()
    query = {"user_id": str(current_user["id"])}
    
    if agent_id: query["agent_id"] = agent_id
    if technique: query["technique"] = technique
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date: query["timestamp"]["$gte"] = start_date
        if end_date: query["timestamp"]["$lte"] = end_date
        
    cursor = attacks_col.find(query).sort("timestamp", -1)
    attacks = await cursor.to_list(length=100)
    for attack in attacks:
        attack["id"] = str(attack.pop("_id"))
    return attacks

@router.get("/{attack_id}", response_model=AttackResponse)
async def get_attack(attack_id: str, current_user: dict = Depends(get_current_user)):
    attacks_col = get_attack_collection()
    attack = await attacks_col.find_one({"attack_id": attack_id, "user_id": str(current_user["id"])})
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    attack["id"] = str(attack.pop("_id"))
    return attack
