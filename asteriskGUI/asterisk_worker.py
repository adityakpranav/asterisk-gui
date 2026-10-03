
import asyncio
from panoramisk import Manager
import config
import datetime

ACTIVE_CALLS = {}
ALL_EXTENSIONS = {}
UPDATE_QUEUE = asyncio.Queue()

ami_manager = Manager(
    host=config.AMI_HOST,
    port=config.AMI_PORT,
    username=config.AMI_USER,
    secret=config.AMI_SECRET
)

# 1. Background worker to catch Asterisk events
async def handle_call_events():
    @ami_manager.register_event('Newchannel')
    def handle_new_channel(manager, event):
        channel = event.get('Channel', 'Unknown')
        caller_num = event.get('CallerIDNum', 'Unknown')
        caller_id = event.get('CallerIDName', 'Unknown')
        
        callee_num = event.get('Exten', 'Unknown')
        callee_id = event.get('ConnectedLineName', ' ')
        channelstate = event.get('ChannelStateDesc', 'Active')
        
        context = event.get('Context', ' ')
        
        if channelstate != "Down":
            ACTIVE_CALLS[channel] = {"caller_num": caller_num, "callee_num": callee_num, "state": "Ringing/Dialing","answered_time": "" ,"Channel":str(channel),"caller_id":caller_id,"callee_id":callee_id,"Context":context}
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    @ami_manager.register_event('Newstate')
    def handle_state_change(manager, event):
        channel = event.get('Channel')
        if channel in ACTIVE_CALLS:
            ACTIVE_CALLS[channel]["state"] = event.get('ChannelStateDesc', 'Active')
            ACTIVE_CALLS[channel]["Channel"] = str(channel)
            ACTIVE_CALLS[channel]["event"] = str(event)
            ACTIVE_CALLS[channel]["callee_id"] = event.get('ConnectedLineName', ' ')
            if ACTIVE_CALLS[channel]["state"].lower() == "up" and ACTIVE_CALLS[channel]["answered_time"] == "":
                ACTIVE_CALLS[channel]["answered_time"] = str(datetime.datetime.now())
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    @ami_manager.register_event('Hangup')
    def handle_hangup(manager, event):
        channel = event.get('Channel')
        if channel in ACTIVE_CALLS:
            del ACTIVE_CALLS[channel]
            asyncio.create_task(UPDATE_QUEUE.put("update"))


    # --- 2. VERBOSE DEBUGGER TRACKER ---
    @ami_manager.register_event('*')
    def debug_all_events(manager, event):
        """Prints every single event structure received to your Uvicorn terminal console logs."""
        evt_name = event.get('event', '')
        if evt_name in ['PeerEntry', 'EndpointList', 'PeerStatus']:
            print(f"DEBUG [Asterisk raw event detected]: {evt_name} -> {dict(event)}")

    # --- 2. LIVE ROSTER & REGISTRATION PACKET HANDLERS ---
    @ami_manager.register_event('EndpointList')
    def handle_pjsip_entry(manager, event):
        """Triggers every time Asterisk streams a PJSIP record entry profile"""
        ext_num = event.get('objectname', '')
        if ext_num and ext_num != 'unknown':
            dev_state = event.get('devicestate', '').lower()
            ALL_EXTENSIONS[ext_num] = {
                "num": ext_num,
                "name": event.get('description') or f"Extension {ext_num}",
                "dept": "Internal PBX",
                "is_registered": dev_state not in ['unavailable', 'unknown', 'invalid']
            }

    @ami_manager.register_event('PeerEntry')
    def handle_legacy_sip_entry(manager, event):
        """Triggers every time Asterisk streams an older chan_sip peer entry"""
        ext_num = event.get('objectname', '')
        if ext_num and ext_num != 'unknown':
            status = event.get('status', '').lower()
            ALL_EXTENSIONS[ext_num] = {
                "num": ext_num,
                "name": f"SIP Line {ext_num}",
                "dept": "Internal PBX",
                "is_registered": "ok" in status or "monitored" in status
            }

    @ami_manager.register_event('PeerStatus')
    def handle_live_status_changes(manager, event):
        """Dynamically patches registrations if a phone reboots or drops out"""
        peer_raw = event.get('peer', '')
        status = event.get('peerstatus', '').lower()
        ext_num = peer_raw.split('/')[-1] if '/' in peer_raw else peer_raw
        if ext_num in ALL_EXTENSIONS:
            ALL_EXTENSIONS[ext_num]["is_registered"] = status in ['registered', 'reachable']

    # Connect to Asterisk console socket
    await ami_manager.connect()
    print("AMI Stream Initialized. Requesting async full core sweep data packets...")
    
    # Send the action once at startup. Asterisk responds to these by broadcasting 
    # 'EndpointList' and 'PeerEntry' events, which our handlers above catch automatically.
    try:
        await ami_manager.send_action({'Action': 'PJSIPShowEndpoints'})
        await ami_manager.send_action({'Action': 'SIPpeers'})
    except Exception as e:
        print(f"Roster initial command dispatch skipped: {e}")

 
    # Stay in an infinite async sleep loop to keep the event listener thread alive
    while True:
        await asyncio.sleep(3600)
