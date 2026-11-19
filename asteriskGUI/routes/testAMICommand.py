

# routes/testAMICommand.py

import asyncio
import json
from fastapi import APIRouter, Request
from schemas import AMICommandRequest
from asterisk_worker import ami_manager
from amiCommandHelper import get_ami_command, execute_ami_command
from .run_script import asterisk_restart , asterisk_status , keepalive_restart, keepalive_status, app_logs
from logger import logger, log_info
from config import TOKEN_USER


# Ensure router is instantiated at top of file if not already
router = APIRouter()

@router.post("/execute-ami")
async def execute_raw_ami_command(payload: AMICommandRequest,request: Request):
    """
    Executes an ad-hoc custom AMI action payload directly against Asterisk.
    Returns the exact key-value string mapping returned by the core telephony engine.
    """
    client_ip = getattr(request.state, "client_ip", "Unknown")
    session_token = request.cookies.get("session_auth_token",None)
    user = TOKEN_USER.get(session_token,None)
    
    logger.info(f"AMI A Triggered | IP: {client_ip} | User : {user} | Command: {payload.command}")
        
    try:
        response = await execute_ami_command(payload)
        return (response)
    except Exception as e:
        print(f"AMI command execution failed: {e}")
        return {"status": "error", "output": f"Execution Error Exception Raised:\n{str(e)}"}

@router.post("/execute-script")
async def execute_raw_script_command(payload: AMICommandRequest,request: Request):
    """
    Executes an ad-hoc custom AMI action payload directly against Asterisk.
    Returns the exact key-value string mapping returned by the core telephony engine.
    """
    #client_ip = getattr(request.state, "client_ip", "Unknown")
    #session_token = request.cookies.get("session_auth_token",None)
    #ser = TOKEN_USER.get(session_token,None)
    #logger.info(f"AMI S Triggered | IP: {client_ip} | User : {user} | Command: {payload.command}")
    log_info(payload,request)

    success, output = "",""
    try:
        if(payload.command["Action"]=="reload_asterisk"):
            success, output = await asterisk_restart()

        elif(payload.command["Action"]=="status_asterisk"):
            success, output = await asterisk_status()

        elif(payload.command["Action"]=="reload_keepalived"):
            success, output = await keepalive_restart()

        elif(payload.command["Action"]=="status_keepalived"):
            success, output = await keepalive_status()

        elif("logs" in payload.command["Action"]):
            success, output = await app_logs(payload.command["Action"].split("_")[1],payload.command["Param"]["Option"],payload.command["Param"]["Value"])


        return {"status": "success", "raw_output": success, "output":output}
    except Exception as e:
        print(f"script command execution failed: {e}")
        return {"status": "error", "output": f"Execution Error Exception Raised:\n{str(e)}"}



    
@router.post("/execute-ami-old")
async def execute_raw_ami_command_old(payload: AMICommandRequest):
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

