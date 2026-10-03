
# routes/streamCall.py

import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas import HangupRequest 

# Import the shared state variables from your background module
from asterisk_worker import ACTIVE_CALLS, UPDATE_QUEUE, ami_manager 

# Create a router instance instead of using @app
router = APIRouter()

@router.get("/stream-calls")
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
@router.post("/disconnect")
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


