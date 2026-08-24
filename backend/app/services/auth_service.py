from fastapi import HTTPException, status
from app.database import get_user_collection
from app.schemas.user import UserCreate
from app.models.user import UserModel
from app.utils.security import get_password_hash

async def create_user(user_in: UserCreate) -> dict:
    users_col = get_user_collection()
    existing_user = await users_col.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    hashed_password = get_password_hash(user_in.password)
    new_user = UserModel(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name
    )
    
    result = await users_col.insert_one(new_user.model_dump(by_alias=True, exclude_none=True))
    created_user = await users_col.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user.pop("_id"))
    return created_user
