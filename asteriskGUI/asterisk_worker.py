
import asyncio
from panoramisk import Manager
import config
import datetime

ACTIVE_CALLS = {}
ACTIVE_CONF = {}
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
        conference = event.get('Conference', '')
        print("@ami_manager.register_event('Newstate') : ********  ",event)
        if channel in ACTIVE_CALLS:
            ACTIVE_CALLS[channel]["state"] = event.get('ChannelStateDesc', 'Active')
            ACTIVE_CALLS[channel]["talking"] = event.get('TalkingStatus', '0')
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

    @ami_manager.register_event('ConfbridgeTalking')
    def handle_confbridge_talking(manager, event):
        channel = event.get('Channel')
        conference = event.get('Conference', '')
        print("@ami_manager.register_event('ConfbridgeTalking') : ********  ",event)
        # TalkingStatus parses as 'on' (Speaking) or '0' (Silent)
        talking_status = event.get('TalkingStatus', '0')
        is_talking = (talking_status == 'on')

        # If the channel is already tracked in active memory, update its metrics
        if channel in ACTIVE_CALLS:
            ACTIVE_CALLS[channel]["talking"] = is_talking
            ACTIVE_CALLS[channel]["conference"] = conference
            
            # Put update directly onto queue to trigger downstream WebSocket broadcast
            asyncio.create_task(UPDATE_QUEUE.put("update"))
        
        # Fallback: If a channel joined a bridge before registering via Newchannel
        else:
            ACTIVE_CALLS[channel] = {
                "caller_num": event.get('CallerIDNum', 'Unknown'),
                "callee_num": event.get('Exten', conference),
                "state": "Up",
                "answered_time": str(datetime.datetime.now()),
                "Channel": str(channel),
                "caller_id": event.get('CallerIDName', 'Unknown'),
                "callee_id": ' ',
                "Context": ' ',
                "talking": is_talking,
                "conference": conference
            }
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    # Connect to Asterisk console socket
    await ami_manager.connect()
    print("AMI Stream Initialized. Requesting async full core sweep data packets...")
    
    # Send the action once at startup. Asterisk responds to these by broadcasting 
    # 'EndpointList' and 'PeerEntry' events, which our handlers above catch automatically.
#    try:
#        await ami_manager.send_action({'Action': 'PJSIPShowEndpoints'})
#        await ami_manager.send_action({'Action': 'SIPpeers'})
#    except Exception as e:
#        print(f"Roster initial command dispatch skipped: {e}")

 
    # Stay in an infinite async sleep loop to keep the event listener thread alive
    while True:
        await asyncio.sleep(3600)
