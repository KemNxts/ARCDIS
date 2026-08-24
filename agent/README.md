# ARCDIS Agent

The ARCDIS Python Agent runs locally on Ubuntu machines to provide continuous behavioral monitoring and prevention against T1059-style attacks (process creation storms and memory abuse).

## Identity Flow

The agent links to a specific user via two tokens in its `.env` file:
1. `AGENT_ID`: A unique identifier for the machine (e.g. `agt_12345`).
2. `USER_TOKEN`: A valid JWT authentication token from the ARCDIS frontend dashboard, proving ownership.

Upon startup, the agent calls `POST /api/agents/register`. The backend extracts the user identity from the `USER_TOKEN` and permanently links the `AGENT_ID` to that user.

## Manual Setup & Testing

If you don't want to install the agent system-wide using systemd, you can run it directly:

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your AGENT_ID and USER_TOKEN
   ```

3. Run the agent (requires `sudo` for cross-user process termination):
   ```bash
   sudo ./venv/bin/python agent.py
   ```

## Production Installation

To install the agent as a persistent background service, simply run the installer script:
```bash
sudo chmod +x install.sh
sudo ./install.sh
```
The script will prompt you for your `AGENT_ID`, `USER_TOKEN`, and `BACKEND_URL`, and automatically configure the systemd service.

## Testing Detection

To verify the agent correctly identifies and blocks the gradual process-spawning attack (`dump.py`):

1. Start the agent using `sudo ./venv/bin/python agent.py`.
2. In another terminal window, run the `dump.py` attack script.
3. Once the script spawns more than 15 children within 10 seconds (default thresholds), the agent will:
   - Identify the parent PID of `dump.py`.
   - Terminate the parent and all its sub-processes immediately.
   - Send an `AttackEvent` telemetry block to your ARCDIS dashboard!
