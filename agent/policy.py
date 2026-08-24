import os
import json
from typing import Dict, Any
from utils import logger

POLICY_PATH = os.path.join(os.path.dirname(__file__), 'policies.json')

class PolicyEngine:
    def __init__(self):
        self.policies = self._load_policies()

    def _load_policies(self) -> list:
        if not os.path.exists(POLICY_PATH):
            logger.error(f"Policy file not found at {POLICY_PATH}. Using empty policies.")
            return []
        try:
            with open(POLICY_PATH, 'r') as f:
                data = json.load(f)
                return data.get("policies", [])
        except Exception as e:
            logger.error(f"Failed to load policies from JSON: {e}")
            return []

    def select_policy(self, risk_tier: str, behavior_type: str = "process_storm") -> Dict[str, Any]:
        """
        Selects the appropriate response policy from the JSON configuration based on the generic risk and behavior.
        """
        for policy in self.policies:
            trigger = policy.get("trigger", {})
            if trigger.get("risk_tier") == risk_tier and trigger.get("behavior_type") in (behavior_type, "any"):
                return policy
                
        # Default fallback policy if nothing matches
        return {
            "id": "pol_default_monitor",
            "action": "MONITOR_ONLY",
            "reason": "No specific policy matched. Defaulting to monitor only."
        }
