from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
