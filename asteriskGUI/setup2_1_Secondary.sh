

echo "[+] Configuring Realtime Sync on Secondary Server..."

sudo apt install unison openssh-client openssh-server -y

echo "[+]  Configuring in Primary Server ...."

# Temporary open login root to server for adding ssh key
# for further logins
SSH_CONFIG="PermitRootLogin yes
PasswordAuthentication yes
"

# Append the lines to /etc/vsftpd.conf safely using sudo tee
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config_bkp
echo "$SSH_CONFIG" | sudo tee -a /etc/ssh/sshd_config

sudo systemctl restart ssh

echo "[+] OPEN Primary Server and run setup2_2_Primary.sh"
read -p "Press [Enter] when Above Script STOPs to continue..."


# Revert Login to Key only and securing the server

sudo cp /etc/ssh/sshd_config_bkp /etc/ssh/sshd_config
echo "PermitRootLogin prohibit-password" | sudo tee -a /etc/ssh/sshd_config
sudo systemctl restart ssh
