
# routes/streamCall.py

import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from schemas import ConfMuteUnmuteRequest, AMICommandRequest
from amiCommandHelper import execute_ami_command
# Import the shared state variables from your background module
#from asterisk_worker import ACTIVE_CONF, UPDATE_QUEUE, ami_manager 

# Create a router instance instead of using @app
router = APIRouter()


'''
# Alternate function to fetch active conf using sockets
# 


@router.get("/stream-conf-calls")
async def stream_conf_calls(request: Request):
    async def event_generator():
        # Always send the initial current state immediately upon load
        #print("stream-conf-calls : ",ACTIVE_CONF)
        yield f"data: {json.dumps(list(ACTIVE_CONF.values()))}\n\n"
        while True:
            if await request.is_disconnected():
                break
            # Wait until an Asterisk state changes, then push new list
            await UPDATE_QUEUE.get()
            yield f"data: {json.dumps(list(ACTIVE_CONF.values()))}\n\n"
            UPDATE_QUEUE.task_done()
    return StreamingResponse(event_generator(), media_type="text/event-stream")
'''


def parse_ami_confbridge_list(raw_messages):
    participants_list = []
    
    # Assuming 'ami_messages' is the raw list of Message objects you received
    for msg in raw_messages:
        # Only process the specific user list events
        if getattr(msg, 'Event', '') == 'ConfbridgeList':
            
            # Build the dictionary directly without any custom classes
            participant = {
                "channel": getattr(msg, 'Channel', ''),
                "callerIdNum": getattr(msg, 'CallerIDNum', ''),
                "callerIdName": getattr(msg, 'CallerIDName', ''),
                "conference": getattr(msg, 'Conference', ''),
                "context": getattr(msg, 'Context', ''),
                "uniqueId": getattr(msg, 'Uniqueid', ''),
                "answeredTimeSeconds": int(getattr(msg, 'AnsweredTime', 0)),
                "isAdmin": 1 if getattr(msg, 'Admin', 'No') == 'Yes' else 0,
                "isMuted": 1 if getattr(msg, 'Muted', 'No') == 'Yes'else 0,
                "isTalking": 1 if getattr(msg, 'Talking', 'No') == 'Yes' else 0,
                "channelState": getattr(msg, 'ChannelStateDesc', 'Unknown')
            }
            participants_list.append(participant)
            
    # Return the pure Python list. FastAPI serializes this automatically!
    return participants_list


import ast
@router.get("/getConfRoomParticipants")
async def getConfRoomParticipants(confRoom: str):
    # FastAPI automatically parses and runs validation using schemas.py rules
    #confRoom = request.args.get["confRoom"]
    print("getConfRoomParticipants : ",confRoom)
    #confRoom = payload.confRoom
    
    if not confRoom:
        return ({"status": "error", "message": "Missing URL query parameter 'confRoom'"})
        
    command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": "conf_room_participants",
                        "Param": {
                            "confRoom": confRoom
                        }
                    }
                ) 
    try:
        raw_output_list = await execute_ami_command(command_payload)

        #print("ConfRoomParticipants : raw_output_list :",len(raw_output_list["output"]),type(raw_output_list["output"]))

        #clean_participants = raw_output_list["output"]
        clean_participants = parse_ami_confbridge_list(raw_output_list["raw_output"])

        
        #print(f"Successfully sent AMI ConfRoomParticipants command for: clean_participants : {clean_participants}")
        return {"status": "success", "message": f"{clean_participants}"}
        
    except Exception as e:
        print(f"Failed sending AMI getConfRoomParticipants action: {str(e)}")
        return {"status": "error", "message": f"Asterisk execution failure: {str(e)}"}


@router.get("/getActiveConfRooms")
async def getActiveConfRooms(request: Request):
    # FastAPI automatically parses and runs validation using schemas.py rules

    command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": "list_active_rooms",
                        "Param": {}
                    }
                ) 
    try:
        response = await execute_ami_command(command_payload)
        response = response["output"]

        print(f"Successfully sent AMI Hangup command for: ConfRoomParticipants : {response}")
        return {"status": "success", "response": f"{response}"}
        
    except Exception as e:
        print(f"Failed sending AMI Mute action: {str(e)}")
        return {"status": "error", "message": f"Asterisk execution failure: {str(e)}"}



# Updated Hangup Route utilizing the external file schema
@router.post("/muteUnmuteConfParticipant")
async def muteUnmuteConfParticipant(request: ConfMuteUnmuteRequest):

    # FastAPI automatically parses and runs validation using schemas.py rules
    channelID = request.channelID
    confRoom = request.confRoom
    muteAction = "mute_conf_participant" if request.isMute == 1 else "unmute_conf_participant"
    command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": muteAction,
                        "Param": {
                            "confRoom": confRoom,
                            "channelID": channelID
                        }
                    }
                ) 

    try:
        #print("muteUnmuteConfParticipant : command_payload : ",command_payload)
        each_response = await execute_ami_command(command_payload)
        each_response = each_response["output"]

        print(f"Successfully sent AMI Hangup command for: {muteAction}")
        return {"status": "success", "message": f"Mute requested for {muteAction}"}
        
    except Exception as e:
        print(f"Failed sending AMI Mute action: {str(e)}")
        return {"status": "error", "message": f"Asterisk execution failure: {str(e)}"}


