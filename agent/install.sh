#!/bin/bash
set -e

# ARCDIS Agent Installation Script
# Must be run as root

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

AGENT_DIR="/opt/arcdis-agent"
LOG_DIR="/var/log/arcdis"

echo "=== ARCDIS Agent Installer ==="

# 1. Prompt for Configuration
read -p "Enter your Agent ID (e.g. agt_...): " AGENT_ID
read -p "Enter your User Auth Token (JWT): " USER_TOKEN
read -p "Enter the ARCDIS Backend URL [http://localhost:8000]: " BACKEND_URL
BACKEND_URL=${BACKEND_URL:-http://localhost:8000}

# 2. Create directories
echo "[*] Creating directories..."
mkdir -p "$AGENT_DIR"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# 3. Install dependencies
echo "[*] Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# 4. Setup Python Environment
echo "[*] Setting up virtual environment..."
python3 -m venv "$AGENT_DIR/venv"
source "$AGENT_DIR/venv/bin/activate"

# Copy source files
echo "[*] Copying source files..."
cp *.py "$AGENT_DIR/"
cp requirements.txt "$AGENT_DIR/"
cp .env.example "$AGENT_DIR/"

# Install Python packages
pip install -r "$AGENT_DIR/requirements.txt"

# 5. Create .env file
echo "[*] Generating configuration..."
cat <<EOF > "$AGENT_DIR/.env"
AGENT_ID="$AGENT_ID"
USER_TOKEN="$USER_TOKEN"
BACKEND_URL="$BACKEND_URL"
HEARTBEAT_INTERVAL=30
MONITOR_INTERVAL=2
MAX_CHILDREN_PER_WINDOW=15
MAX_CHILD_MEMORY_MB=500.0
SPAWN_WINDOW_SECONDS=10
EOF

chmod 600 "$AGENT_DIR/.env"

# 6. Install Systemd Service
echo "[*] Installing systemd service..."
cp arcdis-agent.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable arcdis-agent.service
systemctl start arcdis-agent.service

echo "=== Installation Complete ==="
echo "The agent is now running in the background."
echo "Check status with: sudo systemctl status arcdis-agent"
echo "View logs with: tail -f /var/log/arcdis/agent.log"
