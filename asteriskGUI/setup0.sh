#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define UI Color Codes
ORANGE='\033[38;5;208m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # Reset

echo -e "${ORANGE}"

echo " ****************** Configuring FTP server **************** "

sudo apt update && sudo apt install -y vsftpd dos2unix ufw 

#Setup ftp Server
sudo systemctl start vsftpd
sudo systemctl enable vsftpd



# Define the configuration block to append
VSFTPD_CONFIG="write_enable=YES
chroot_local_user=YES
allow_writeable_chroot=YES
local_root=/

pasv_enable=YES
pasv_min_port=40000
pasv_max_port=50000
"

# Append the lines to /etc/vsftpd.conf safely using sudo tee
echo "$VSFTPD_CONFIG" | sudo tee -a /etc/vsftpd.conf


sudo ufw allow 20/tcp
sudo ufw allow 21/tcp
sudo ufw allow 123/udp
sudo ufw allow 5060/udp
sudo ufw allow 40000:50000/tcp
#sudo ufw reload
sudo systemctl restart vsftpd 

echo "**************  vsftpd configuration updated successfully.*********************"
sudo chmod -R 777 "$PWD"

#cp -r asterisk_util/asterisk /etc/asterisk

echo -e "${CYAN}┌─────────────────────────────────────────────────────────────────────────────┐"
echo -e "|************  Copy required files in /home/<user> folder and then run  *************|"
echo -e "│${WHITE}  DIR: asteriskGUI (Paste Server Files Here)                         ${CYAN}│"
echo -e "│${WHITE}  bash setup1.sh                                                     ${CYAN}│"
echo -e "└────────────────────────────────────────────────────────────────────────────────────┘"


