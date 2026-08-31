import requests
import time
import threading
from config import config
from models import AgentRegistration, AttackEvent
from utils import logger

class Reporter:
    def __init__(self):
        self.base_url = config.BACKEND_URL
        self.agent_id = config.AGENT_ID
        self.headers = {
            "X-User-Id": config.USER_ID,
            "Content-Type": "application/json"
        }
        self.heartbeat_thread = None
        self.running = False

    def register(self) -> bool:
        """Register the agent with the backend."""
        logger.info(f"Registering agent {self.agent_id} with ARCDIS backend...")
        reg_data = AgentRegistration(
            agent_id=self.agent_id,
            hostname=config.HOSTNAME,
            os_info=config.OS_INFO,
            version=config.AGENT_VERSION
        )
        
        try:
            response = requests.post(
                f"{self.base_url}/api/agents/register",
                headers=self.headers,
                json=reg_data.to_dict(),
                timeout=10
            )
            # 201 Created or 400 Bad Request (if already registered, which is fine)
            if response.status_code in (201, 400):
                logger.info("Agent registration successful (or already registered).")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Registration request failed: {e}")
            return False

    def send_attack_event(self, event: AttackEvent):
        """Send an attack telemetry event to the backend."""
        try:
            response = requests.post(
                f"{self.base_url}/api/attacks",
                headers=self.headers,
                json=event.to_dict(),
                timeout=5
            )
            if response.status_code == 201:
                logger.info("Attack event reported to backend successfully.")
            else:
                logger.error(f"Failed to report attack event: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send attack event (network error): {e}")

    def _heartbeat_loop(self):
        """Background loop to send periodic heartbeats."""
        while self.running:
            try:
                response = requests.patch(
                    f"{self.base_url}/api/agents/{self.agent_id}/heartbeat",
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code != 200:
                    logger.warning(f"Heartbeat failed: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                logger.debug(f"Heartbeat network error: {e}")
            
            time.sleep(config.HEARTBEAT_INTERVAL)

    def start_heartbeat(self):
        """Start the background heartbeat thread."""
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        logger.info(f"Heartbeat thread started ({config.HEARTBEAT_INTERVAL}s interval).")

    def stop_heartbeat(self):
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
