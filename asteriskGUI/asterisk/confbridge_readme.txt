

; extensions
exten => 105,1,NoOp(Entering Conference Room 105)
 same => n,Answer()
 same => n,Playback(welcome)
 same => n,ConfBridge(105,default_bridge,default_user)
 same => n,Hangup()

; confbridge
[default_bridge]
type=bridge
max_members=20
internal_sample_rate=auto

[default_user]
type=user
music_on_hold_when_empty=yes
music_on_hold_class=default
announce_join_leave=no

[105](default_bridge)
[109](default_bridge)


	sudo tail -n 50 /var/log/asterisk/messages.log | grep confbridge


	asterisk -rx "module reload app_confbridge.so"
 
	confbridge show profile bridge(s)/user(s) 
 
	confbridge list
	 
	   Conference Bridge Name           Users  Marked Locked Muted
      ================================ ====== ====== ====== =====
       101                                   1      0 No     No


	confbridge kick <conference> <channel>/all
	
	confbridge mute/unmute <conference> <channel>/all