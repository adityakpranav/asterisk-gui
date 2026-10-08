#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

sudo chmod -R 777 "$PWD"

# Define UI Color Codes
ORANGE='\033[38;5;208m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # Reset

echo -e "${ORANGE}"
cat << "EOF"
         ,---.
			   _   _ _____ ____  
			  | \ | | ____|  _ \ 
			  |  \| |  _| | |_) |
			  | |\  | |___|  _ < 
			  |_| \_|_____|_| \_\
 				    _         _                  _      ___ _   _ ___ 
                  / \   ___  | |_ ___ _ __(_)___| | __/ ___| | | |_ _|
                / _ \ / __| | __/ _ \ '__| / __| |/ / |  _| | | || | 
               / ___ \\__ \ | ||  __/ |  | \__ \   <| |_| | |_| || | 
              /_/   \_\___/ \__\___|_|  |_| ___/_ |\_\\____|\___/|__|
              
       
EOF
echo -e "${CYAN}┌────────────────────────────────────────────────────────┐"
echo -e "│${WHITE}  Asterisk PBX Manager  ${CYAN}                        │"
echo -e "└────────────────────────────────────────────────────────────────┘"
echo -e "${GRAY}                    » created by GKP Exchange NER «${NC}\n"



echo " Current Working DIR : $PWD"

cat << "EOF"
         ,---.
				Installing Asterisk and Setup Configuration
EOF


echo -e "${ORANGE} [+] Checking If required file Exist ..."

FOLDER_NAME="asteriskGUI"
HOME_DIR="/home"
# Search for the directory name recursively inside /home
RESULT=$(find "$HOME_DIR" -type d -name "$FOLDER_NAME" -print -quit)

# If the folder path is empty, it means the folder does not exist
if [ -z "$RESULT" ]; then
    echo "Error: Folder '$FOLDER_NAME' does not exist in /home. Exiting script."
    exit 1
fi

echo " ****************** Installing Required files **************** "

sudo apt install -y \
		asterisk sngrep keepalived build-essential
sudo apt autoremove -y


echo " ****************  Check Asterisk Version Details **************** "

asterisk -rx "core show version"

echo " ****************  Applying asterisk Configuration from backup **************** "



# 2. Configure Asterisk RealTime DB
echo "[+] Configuring Asterisk 21 Engine..."

sudo cp asterisk/pjsip.conf /etc/asterisk/pjsip.conf
sudo cp asterisk/pjsip_wizard.conf /etc/asterisk/pjsip_wizard.conf
sudo cp asterisk/extensions.conf /etc/asterisk/extensions.conf
sudo cp asterisk/logger.conf /etc/asterisk/logger.conf
sudo cp asterisk/manager.conf /etc/asterisk/manager.conf

# 3. Allow Asterisk to Bind to a "Non-Local" IP
sudo sysctl -w net.ipv4.ip_nonlocal_bind=1

echo "net.ipv4.ip_nonlocal_bind = 1" | sudo tee -a /etc/sysctl.conf

sudo sysctl -p

#keepalived config 
PRIMARY_IP="10.24.49.192"
SECONDARY_IP="10.24.49.193"
LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}')

# Determine local system operational cluster roles
if [ "$LOCAL_IP" == "$PRIMARY_IP" ]; then
	sudo cp keepalived/keepalived_server1.conf /etc/keepalived/keepalived.conf
	sudo cp asterisk/dashboardv1_server1.service /etc/systemd/system/dashboardv1.service
    echo "👑 System matches PRIMARY IP configuration template."
elif [ "$LOCAL_IP" == "$SECONDARY_IP" ]; then
	sudo cp keepalived/keepalived_server2.conf /etc/keepalived/keepalived.conf
	sudo cp asterisk/dashboardv1_server2.service /etc/systemd/system/dashboardv1.service
    echo "🛡️  System matches SECONDARY IP configuration template."
else
    echo "❌ Error: System IP ($LOCAL_IP) does not match Primary ($PRIMARY_IP) or Secondary ($SECONDARY_IP)."
    exit 1
fi


sudo bash keepalived/health-check-scripts.sh

sudo chown root:root /etc/keepalived/keepalived.conf
sudo chmod 644 /etc/keepalived/keepalived.conf
sudo ufw allow 8000/tcp


sudo systemctl enable keepalived
sudo systemctl start keepalived
sudo journalctl -u keepalived -n 20


# check asterisk port
sudo systemctl restart asterisk
sudo ss -lnpup | grep asterisk

# Check if endpoints are online
sudo asterisk -rx "pjsip show endpoints"

echo "[+] Configuring NTP Server..."
sudo bash datetime_config.sh


echo " ****************  Check Asterisk Version Details **************** "

# 2. Check the exit code immediately
if [ $? -eq 0 ]; then
    echo "✅ Configuration applyed successfully "
else
    echo "❌ Error: applying configuration !"
    exit 1
fi


echo " ****************  Python 3.14 Setup **************** "

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚙️ 'uv' not found. Installing uv (fast Python manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source the cargo/env or local path if uv installation modified it
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Creating virtual environment with Python 3.14..."
uv venv pyasterisk --python 3.14 --seed

echo "Virtual environment successfully created in 'pyasterisk/'!"
echo "Installing dependencies>>>>>>>>>"

# pyasterisk_bkp/bin/python3 -m pip freeze
echo $PWD
pyasterisk/bin/python3 -m pip install -r requirement.txt

echo "Dependency installed successfully in Virtual Env"
echo "Checking server Status (Ctrl+C to close)>>>>>>"

echo "Configuring dashboard service......"
# Configure asteriskGUI service
sudo systemctl enable dashboardv1.service
sudo systemctl daemon-reload
sudo systemctl enable dashboardv1.service
sudo systemctl start dashboardv1.service
sudo journalctl -u dashboardv1.service -n 20 



