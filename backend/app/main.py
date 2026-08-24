from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.middleware.cors import setup_cors
from app.routes import auth, users, agents, attacks

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

setup_cors(app)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["agents"])
app.include_router(attacks.router, prefix=f"{settings.API_V1_STR}/attacks", tags=["attacks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ARCDIS API"}
