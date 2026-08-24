from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Ensure indexes on startup
    database = db.client[settings.DATABASE_NAME]
    
    # User indexes
    await database.users.create_index("email", unique=True)
    
    # Agent indexes
    await database.agents.create_index("agent_id", unique=True)
    await database.agents.create_index("user_id")
    
    # Attack indexes
    await database.attacks.create_index("agent_id")
    await database.attacks.create_index("user_id")

async def close_mongo_connection():
    if db.client is not None:
        db.client.close()

def get_database():
    return db.client[settings.DATABASE_NAME]
def get_user_collection():
    return db.client[settings.DATABASE_NAME].users
def get_agent_collection():
    return db.client[settings.DATABASE_NAME].agents
def get_attack_collection():
    return db.client[settings.DATABASE_NAME].attacks
