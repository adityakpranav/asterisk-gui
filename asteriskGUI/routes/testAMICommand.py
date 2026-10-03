

# routes/testAMICommand.py

import asyncio
import json
from fastapi import APIRouter, HTTPException
from schemas import AMICommandRequest
from asterisk_worker import ami_manager
from amiCommandHelper import get_ami_command

# Ensure router is instantiated at top of file if not already
router = APIRouter()

@router.post("/execute-ami")
async def execute_raw_ami_command(payload: AMICommandRequest):
    """
    Executes an ad-hoc custom AMI action payload directly against Asterisk.
    Returns the exact key-value string mapping returned by the core telephony engine.
    """
    try:
        # 1. Fire the custom payload map dict directly over the network socket channel
        #payload.action = json.loads(payload.action)
        #print("payload.command : ",payload.command,type(payload.command))
        if(payload.dc == "Y"):
            response = await ami_manager.send_action(payload.command)
        else:
            #print("payload.command['Action'] :",payload.command["Action"])
            cmd_check = get_ami_command(payload.command["Action"],payload.command["Param"])
            print(cmd_check)
            response = await ami_manager.send_action(cmd_check)
            
        
        # 2. Package response structure attributes dynamically
        # panoramisk responses contain internal .headers dictionary parameters
        print("response : ",type(response),response)

        try:
            return {"status": "success", "output": json.dumps(response.as_dict(), indent=4)}
        except:
            return {"status": "success", "output": str(response)}
            
    except Exception as e:
        print(f"AMI command execution failed: {e}")
        return {"status": "error", "output": f"Execution Error Exception Raised:\n{str(e)}"}

