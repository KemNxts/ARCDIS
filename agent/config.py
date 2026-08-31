import os
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Identity
    AGENT_ID = os.getenv("AGENT_ID", "")
    USER_ID = os.getenv("USER_ID", "")
    
    # System Info
    HOSTNAME = platform.node()
    OS_INFO = f"{platform.system()} {platform.release()} ({platform.version()})"
    AGENT_VERSION = "1.0.0"

    # API
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip('/')
    
    # Timings
    HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", 30))
    MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", 2))
    
    # Detection Thresholds
    MAX_CHILDREN_PER_WINDOW = int(os.getenv("MAX_CHILDREN_PER_WINDOW", 15))
    MAX_CHILD_MEMORY_MB = float(os.getenv("MAX_CHILD_MEMORY_MB", 500.0))
    SPAWN_WINDOW_SECONDS = int(os.getenv("SPAWN_WINDOW_SECONDS", 10))

    @classmethod
    def validate(cls):
        if not cls.AGENT_ID:
            raise ValueError("AGENT_ID must be set in .env")
        if not cls.USER_ID:
            raise ValueError("USER_ID must be set in .env")

config = Config()
