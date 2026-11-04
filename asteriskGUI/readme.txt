##### Welcome to asterisk GUI########

#### This is apython based GUI server for Asterisk 21
#### This asteriskGUI Server lets you perform basic operations on the server

## Setup

# 1. Install Ubuntu
# 2. Login to server cli and navigate to directory "/home/<user>" 
# 3. Create file server 
#		a). Copy content of setup0.sh
#		b). create file in server :nano setup0.sh
#		c). paste content of setup0.sh (local) into setup0.sh (server)
# 4. Login with WinSCP in server and Paste asteriskGUI(local) in Server path 
# 5. Change Permissions for /home directory "sudo chmod -R 777 "$PWD"
# 6. Convert setup1.sh in required format : "dos2unix setup1.sh"
# 7. Then Run : "bash setup1.sh"

##### Reinstall Errors 
### Realtime Sync : create SSH key again in both server
## 
## (S1 & S2)File : nano /etc/ssh/sshd_config 
## Change: 
##           #PermitRootLogin prohibit-password
##            PermitRootLogin yes
##            PasswordAuthentication yes
##

### clean ssh-keygen history in both server 
##  S1 : sudo ssh-keygen -f '/root/.ssh/known_hosts' -R '< S2 IP >'
##  S2 : sudo ssh-keygen -f '/root/.ssh/known_hosts' -R '< S1 IP >'
##

### setup history in both server 
## sudo unison asterisk_sync





