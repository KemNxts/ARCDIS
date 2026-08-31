from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from fastapi.responses import StreamingResponse
import io
import zipfile
import os
from app.schemas.agent import AgentRegister, AgentResponse, AgentHeartbeatResponse
from app.services.agent_service import register_agent, update_agent_heartbeat
from app.utils.dependencies import get_current_user, get_agent_identity
from app.database import get_agent_collection

router = APIRouter()

@router.get("/download")
async def download_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    zip_buffer = io.BytesIO()
    
    agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent"))
    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=500, detail="Agent source directory not found")
        
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, dirs, files in os.walk(agent_dir):
            # Prune unwanted directories
            dirs[:] = [d for d in dirs if d not in (".git", "venv", "__pycache__", "scratch")]
            for file in files:
                if file in [".env", ".env.example", ".gitignore", "agent.log", "install.sh", "start.sh", "arcdis-agent.service"]:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, agent_dir)
                zip_file.write(file_path, os.path.join("arcdis_agent", arcname))
                
        # Generate dynamic .env file with both USER_ID and AGENT_ID
        env_content = f"BACKEND_URL=http://localhost:8000\nUSER_ID={user_id}\nAGENT_ID={agent_id}\nMONITOR_INTERVAL=2\n"
        zip_file.writestr("arcdis_agent/.env", env_content)
        
        # Add install script
        install_script = """#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo bash install.sh)"
  exit
fi

echo "[+] Installing ARCDIS Agent for Ubuntu..."
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Setup virtual environment as the regular user to avoid root-owned files in venv
SUDO_USER_NAME=${SUDO_USER:-root}
sudo -u $SUDO_USER_NAME python3 -m venv $DIR/venv
sudo -u $SUDO_USER_NAME $DIR/venv/bin/pip install -r $DIR/requirements.txt

# Create systemd service
cat <<EOF > /etc/systemd/system/arcdis-agent.service
[Unit]
Description=ARCDIS IPS Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=$DIR/venv/bin/python $DIR/agent.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable arcdis-agent
systemctl start arcdis-agent

echo "[+] Installation complete. Agent is now running as a startup application."
echo "[+] Check status with: sudo systemctl status arcdis-agent"
"""
        zip_file.writestr("arcdis_agent/install.sh", install_script)

        
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": "attachment; filename=arcdis_agent.zip"}
    )


@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register(agent_in: AgentRegister, current_user: dict = Depends(get_agent_identity)):
    return await register_agent(str(current_user["id"]), agent_in)

@router.get("", response_model=List[AgentResponse])
async def list_agents(current_user: dict = Depends(get_current_user)):
    agents_col = get_agent_collection()
    cursor = agents_col.find({"user_id": str(current_user["id"])})
    agents = await cursor.to_list(length=100)
    for agent in agents:
        agent["id"] = str(agent.pop("_id"))
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    agents_col = get_agent_collection()
    agent = await agents_col.find_one({"agent_id": agent_id, "user_id": str(current_user["id"])})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent["id"] = str(agent.pop("_id"))
    return agent

@router.patch("/{agent_id}/heartbeat", response_model=AgentHeartbeatResponse)
async def heartbeat(agent_id: str, current_user: dict = Depends(get_agent_identity)):
    return await update_agent_heartbeat(str(current_user["id"]), agent_id)
