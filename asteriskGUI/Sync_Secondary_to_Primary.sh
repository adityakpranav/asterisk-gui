#!/bin/bash

REMOTE_SSH_SERVER="root@10.24.49.192"

echo "[+] SYNC Secondary to Primary ...... "
sudo unison asterisk_sync


ssh $REMOTE_SSH_SERVER "asterisk -rx 'core reload' "
# Push Chenges to Secondary Server

# If Unison finishes successfully (Exit code 0), trigger Asterisk reloads on both nodes
if [ $? -eq 0 ]; then
    # Reload Local Primary Asterisk
    ssh $REMOTE_SSH_SERVER "chmod 777 /etc/asterisk/ -R"
fi

