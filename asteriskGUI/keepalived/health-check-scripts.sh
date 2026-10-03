#!/bin/bash
# Deploy each function below as its own file in /usr/local/bin/ on BOTH servers,
# chmod +x each one. Referenced by keepalived.conf vrrp_script blocks.

############################################
# /usr/local/bin/chk_asterisk.sh
############################################
cat <<'EOF' > /usr/local/bin/chk_asterisk.sh
#!/bin/bash
# Returns 0 (OK) if asterisk CLI/manager responds
asterisk -rx "core show uptime" >/dev/null 2>&1
exit $?
EOF
chmod +x /usr/local/bin/chk_asterisk.sh

############################################
# /usr/local/bin/notify_master.sh  (VIP acquired -> become active)
############################################
cat <<'EOF' > /usr/local/bin/notify_master.sh
#!/bin/bash
logger "keepalived: transitioning to MASTER - VIP acquired"
# Optionally: bump this node's dispatcher priority, warm caches, etc.
EOF
chmod +x /usr/local/bin/notify_master.sh

############################################
# /usr/local/bin/notify_backup.sh
############################################
cat <<'EOF' > /usr/local/bin/notify_backup.sh
#!/bin/bash
logger "keepalived: transitioning to BACKUP - VIP released"
EOF
chmod +x /usr/local/bin/notify_backup.sh

############################################
# /usr/local/bin/notify_fault.sh
############################################
cat <<'EOF' > /usr/local/bin/notify_fault.sh
#!/bin/bash
logger "keepalived: FAULT state - health check failed"
EOF
chmod +x /usr/local/bin/notify_fault.sh

echo "All health-check + notify scripts installed to /usr/local/bin/"
