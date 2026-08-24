from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from app.models import PyObjectId

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    hashed_password: str
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
