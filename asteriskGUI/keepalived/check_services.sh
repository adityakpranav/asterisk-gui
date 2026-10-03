#!/bin/bash
# ====================================================================
# Keepalived Health Check Script for Asterisk HA & Kamailio
# Log Output Tag: vrrp_asterisk_ha
# ====================================================================

LOG_TAG="vrrp_asterisk_ha"

# 1. Verify Kamailio Process
if ! pgrep -x "kamailio" > /dev/null; then
    echo "$(date) [ERROR] Kamailio service process is NOT running" | logger -p 3 -t $LOG_TAG
    exit 1
fi

# 2. Verify Asterisk Process
if ! pgrep -x "asterisk" > /dev/null; then
    echo "$(date) [ERROR] Asterisk service process is NOT running" | logger -p 3 -t $LOG_TAG
    exit 1
fi

# 3. Check Kamailio SIP Port 5060 responsiveness via sipsak or nc
if ! nc -z -u -w 2 127.0.0.1 5060 > /dev/null 2>&1; then
    echo "$(date) [WARNING] Kamailio SIP port 5060 UDP is non-responsive" | logger -p 4 -t $LOG_TAG
    exit 1
fi

# 4. Check Redis Server availability
if ! redis-cli ping | grep -q "PONG"; then
    echo "$(date) [WARNING] Redis server ping failed" | logger -p 4 -t $LOG_TAG
    exit 1
fi

echo "$(date) [OK] All HA services (Kamailio, Asterisk, Redis) healthy" | logger -p 7 -t $LOG_TAG
exit 0
