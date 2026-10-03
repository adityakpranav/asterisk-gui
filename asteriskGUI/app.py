#app.py

import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from panoramisk import Manager
from fastapi.templating import Jinja2Templates
import datetime
from pydantic import BaseModel
from schemas import HangupRequest 

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Global dictionary to track active calls {channel_id: call_details}
ACTIVE_CALLS = {}
# Modern queue to push live updates to the webpage
UPDATE_QUEUE = asyncio.Queue()

# Setup Asterisk AMI client connection
# Panoramisk handles the async reading of PBX streams seamlessly
ami_manager = Manager(
    host="127.0.0.1",
    port=5038,
    username="exch_gui",
    secret="exch@63974"
)

# 1. Background worker to catch Asterisk events
async def handle_call_events():
    @ami_manager.register_event('Newchannel')
    def handle_new_channel(manager, event):
        channel = event.get('Channel', 'Unknown')
        caller_id = event.get('CallerIDNum', 'Unknown')
        callee_id = event.get('Exten', 'Unknown')
        channelstate = event.get('ChannelStateDesc', 'Active')
        if channelstate != "Down":
            ACTIVE_CALLS[channel] = {"caller_id": caller_id, "callee_id": callee_id, "state": "Ringing/Dialing","answered_time": "" ,"Channel":str(channel)}
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    @ami_manager.register_event('Newstate')
    def handle_state_change(manager, event):
        channel = event.get('Channel')
        if channel in ACTIVE_CALLS:
            ACTIVE_CALLS[channel]["state"] = event.get('ChannelStateDesc', 'Active')
            ACTIVE_CALLS[channel]["Channel"] = str(channel)
            ACTIVE_CALLS[channel]["event"] = str(event)
            if ACTIVE_CALLS[channel]["state"].lower() == "up" and ACTIVE_CALLS[channel]["answered_time"] == "":
                ACTIVE_CALLS[channel]["answered_time"] = str(datetime.datetime.now())
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    @ami_manager.register_event('Hangup')
    def handle_hangup(manager, event):
        channel = event.get('Channel')
        if channel in ACTIVE_CALLS:
            del ACTIVE_CALLS[channel]
            asyncio.create_task(UPDATE_QUEUE.put("update"))

    await ami_manager.connect()
    # Stay in an infinite async sleep loop to keep the event listener thread alive
    while True:
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    # Start tracking channels as soon as the webserver spins up
    asyncio.create_task(handle_call_events())

# 2. Server-Sent Events (SSE) Route for instant browser UI refreshes
@app.get("/stream-calls")
async def stream_calls(request: Request):
    async def event_generator():
        # Always send the initial current state immediately upon load
        yield f"data: {json.dumps(list(ACTIVE_CALLS.values()))}\n\n"
        while True:
            if await request.is_disconnected():
                break
            # Wait until an Asterisk state changes, then push new list
            await UPDATE_QUEUE.get()
            yield f"data: {json.dumps(list(ACTIVE_CALLS.values()))}\n\n"
            UPDATE_QUEUE.task_done()
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Updated Hangup Route utilizing the external file schema
@app.post("/disconnect")
async def disconnect_call(request: HangupRequest):
    # FastAPI automatically parses and runs validation using schemas.py rules
    channel_to_kill = request.channel
    
    if channel_to_kill not in ACTIVE_CALLS:
        return {"status": "error", "message": f"Channel {channel_to_kill} not active or already dropped."}
        
    try:
        await ami_manager.send_action({
            'Action': 'Hangup',
            'Channel': channel_to_kill
        })
        print(f"Successfully sent AMI Hangup command for: {channel_to_kill}")
        return {"status": "success", "message": f"Hangup requested for {channel_to_kill}"}
        
    except Exception as e:
        print(f"Failed sending AMI Hangup action: {str(e)}")
        return {"status": "error", "message": f"Asterisk execution failure: {str(e)}"}


# 3. Main Webpage Interface Layout
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index_test.html", 
        context={"title": "Asterisk Active Calls", "status": "Connected"}
    )
    

