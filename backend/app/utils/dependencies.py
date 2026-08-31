from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from app.schemas.token import TokenData
from app.database import get_user_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    users_col = get_user_collection()
    user = await users_col.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
        
    user["id"] = str(user.pop("_id"))
    return user

from fastapi import Header

async def get_agent_identity(x_user_id: str = Header(None, alias="X-User-Id")):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
        
    users_col = get_user_collection()
    from bson import ObjectId
    try:
        user = await users_col.find_one({"_id": ObjectId(x_user_id)})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
        
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    user["id"] = str(user.pop("_id"))
    return user
