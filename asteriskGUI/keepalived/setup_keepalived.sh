
sudo chmod -R 777 "$PWD"
#keepalived config 
PRIMARY_IP="10.24.49.192"
SECONDARY_IP="10.24.49.193"
LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}')

# Determine local system operational cluster roles
if [ "$LOCAL_IP" == "$PRIMARY_IP" ]; then
	sudo cp keepalived/keepalived_server1.conf /etc/keepalived/keepalived.conf
    echo "👑 System matches PRIMARY IP configuration template."
elif [ "$LOCAL_IP" == "$SECONDARY_IP" ]; then
	sudo cp keepalived/keepalived_server2.conf /etc/keepalived/keepalived.conf
    echo "🛡️  System matches SECONDARY IP configuration template."
else
    echo "❌ Error: System IP ($LOCAL_IP) does not match Primary ($PRIMARY_IP) or Secondary ($SECONDARY_IP)."
    exit 1
fi


sudo bash health-check-scripts.sh
sudo systemctl enable keepalived
sudo systemctl start keepalived
sudo journalctl -u keepalived -n 20



