#!/bin/bash

echo "[+] Installing and Configuring NTP Server"

sudo apt install ufw chrony -y

sudo ufw allow 123/udp

sudo timedatectl set-timezone Asia/Kolkata


# Define the configuration block to append
CHRONY_CONFIG="# Syncing to a specific individual NTP server
server 216.239.35.0 iburst
server 14.139.60.103 iburst
#
# Allow access from a specific subnet
allow 10.24.0.0/16
"

# Append the lines to /etc/chrony.conf safely using sudo tee
echo "$CHRONY_CONFIG" | sudo tee -a /etc/chrony/chrony.conf

sudo systemctl restart chrony
sudo systemctl enable chrony
sudo chronyc makestep


chronyc sources

## tracking time
echo "[+] Checking NTP Server"
chronyc tracking

sudo date

sudo timedatectl set-local-rtc 0