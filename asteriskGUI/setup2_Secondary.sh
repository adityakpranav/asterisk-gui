

echo "[+] Configuring Realtime Sync..."
echo "[+]  Configuring in Secondary Server ...."
echo " Generate an SSH key pair (hit Enter through all prompts to keep passphrase blank):"

# Target Secondary Server
REMOTE_SERVER="root@10.24.49.192"

sudo ssh-keygen -t rsa -b 4096

echo "[+] Type the correct root password for 10.24.49.192 when prompted. It should successfully report that 1 key was added."
ssh-copy-id $REMOTE_SERVER

echo "******************   type exit when logged into Secondary Server ********"
#ssh $SECONDARY_SERVER "exit"
ssh $REMOTE_SERVER "sudo cp /etc/ssh/sshd_config_bkp /etc/ssh/sshd_config && echo 'PermitRootLogin prohibit-password' | sudo tee -a /etc/ssh/sshd_config && sudo systemctl restart ssh"


# Ask the user a question
read -p "Did you get access to Secondary Server? (y/n): " choice

# Check the input using an if-else condition
if [ "$choice" = "n" ] || [ "$choice" = "N" ]; then
    echo "Exiting script. Goodbye!"
    exit 0
else
    echo "Continuing with the script..."
fi


sudo mkdir -p ~/.unison
UNISON_PROFILE_PATH="$HOME/.unison/asterisk.prf" 
mkdir -p "$(dirname "$UNISON_PROFILE_PATH")"


SYNC_CONFIG="# Roots of the synchronization (Local and Remote)
root = /etc/asterisk
root = ssh://$REMOTE_SERVER//etc/asterisk

# Paths to explicitly include (keeps the rest of /etc/asterisk ignored)
path = extensions.conf
path = pjsip_wizard.conf

# Automation and Silencing settings
auto = true
batch = true

# Conflict Resolution: In case of simultaneous edits, keep the newer file
prefer = newer

# Maintain original file permissions and ownership rules
perms = 0"

echo "$SYNC_CONFIG" | sudo tee -a ~/.unison/asterisk_sync.prf
echo "SERVER_DIR = '$PWD'" | sudo tee -a config.py

# Perform First Sync
echo "[+] SYNC "
sudo cp Sync_Secondary_to_Primary.sh routes/sync_asterisk.sh
chmod +x $PWD/routes/sync_asterisk.sh
sudo bash routes/sync_asterisk.sh

