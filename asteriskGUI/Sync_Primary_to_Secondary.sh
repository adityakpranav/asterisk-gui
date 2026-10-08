

REMOTE_SSH_SERVER="root@10.24.49.193"

echo "[+] SYNC Primary to Secondary ...... "
sudo unison asterisk_sync

# Push Chenges to Secondary Server

# If Unison finishes successfully (Exit code 0), trigger Asterisk reloads on both nodes
if [ $? -eq 0 ]; then
    # Reload Local Primary Asterisk
    asterisk -rx "dialplan reload" && asterisk -rx "pjsip reload"

    # Reload Remote Secondary Asterisk over SSH
    ssh $REMOTE_SSH_SERVER "asterisk -rx 'dialplan reload' && asterisk -rx 'pjsip reload'"
fi

