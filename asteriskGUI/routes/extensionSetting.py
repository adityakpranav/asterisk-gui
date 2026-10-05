

# routes/extensionSetting.py

import asyncio
import json
from fastapi import APIRouter, HTTPException
from schemas import AMICommandRequest, ExtensionCreateRequest, ExtensionModifyRequest, ExtensionDeleteRequest
from asterisk_worker import ami_manager
from amiCommandHelper import get_ami_command

# Ensure router is instantiated at top of file if not already
router = APIRouter()

# --- CREATE EXTENSION ---
@router.post("/extension/create")
async def create_new_extension(payload: ExtensionCreateRequest):
    try:
        
        numStart = int(payload.numStart)
        numEnd = payload.numEnd
        
        all_response = {}
        if numEnd:
            # Bulk Extension Creation
            numEnd = int(numEnd)
            for eachNum in range(numStart,numEnd+1,1):
                
                # Update Extension PJSIP_wizard.conf
                
                command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": "create_extension",
                        "Param": {
                            "context-template": payload.dept, 
                            "context": payload.dept.split("-")[0],
                            "extension": eachNum,                  
                            "password": payload.passwd,
                            "callerid": eachNum
                        }
                    }
                ) 
                
                each_response = await execute_ami_command(command_payload)
                all_response[eachNum] = each_response["output"]
                
                # Dialplan Update
                command_payload.command["Action"] = "create_dialplan"
                each_response = await execute_ami_command(command_payload)
                    
            print("all_response : ",all_response)
            print("Extension Created Successfully")
            
            command_payload.command["Action"] = "reload_pjsip"
            await execute_ami_command(command_payload)
            
            command_payload.command["Action"] = "reload_dialplan"
            await execute_ami_command(command_payload)
                        
            return {"status": "success", "message": f"Extension from {numStart} to {eachNum} successfully created in PBX pool configuration context.","response":all_response}      
        else:
        
            # Creation of 1 Extension
            command_payload = AMICommandRequest(
                dc="N",
                command={
                    "Action": "create_extension",
                    "Param": {
                        "context-template": payload.dept, 
                        "context": payload.dept.split("-")[0],
                        "extension": numStart,                  
                        "password": payload.passwd,
                        "callerid": payload.callerid
                    }
                }
            ) 
            
            each_response = await execute_ami_command(command_payload)
            all_response[numStart] = each_response["output"]
            
            print("all_response : ",all_response)
            
            # Dialplan Update
            command_payload.command["Action"] = "create_dialplan"
            each_response = await execute_ami_command(command_payload)
            
            print("Extension Created Successfully")
            
            command_payload.command["Action"] = "reload_pjsip"
            await execute_ami_command(command_payload)
            
            command_payload.command["Action"] = "reload_dialplan"
            await execute_ami_command(command_payload)
            
            
            return {"status": "success", "response": f"Extension {numStart} successfully created in PBX pool configuration context.","message":str(all_response)}
    except Exception as e:
        return {"status": "error", "message": f"Backend pipeline creation error exception: {str(e)}"}

# --- MODIFY EXTENSION ---
@router.post("/extension/modify")
async def modify_existing_extension(payload: ExtensionModifyRequest):    
    
    all_response = {}
    update_val = {}
    # payload parse
    try:
        
        num = int(payload.numStart)
        dept = payload.dept
        update_val["callerid"] = payload.callerid
        update_val["password"] = payload.passwd
        
    except Exception as e:
        return {"status": "error", "message": f"Backend pipeline creation error exception: {str(e)}"}

        
    try:
        for key, val in update_val.items():
            # Update available values ID
            if val:
                command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": f"modify_extension_{key}",
                        "Param": {
                            "context-template": dept, 
                            "extension": num,                  
                            key: val
                        }
                    }
                ) 
                
                each_response = await execute_ami_command(command_payload)
                all_response[key] = each_response["output"]
        
        print("all_response : ",all_response) 
        print("Extension Modified Successfully")
        
        # Reload PJSIP and Dialplan
        command_payload = AMICommandRequest(dc="N",command={"Action": "reload_pjsip","Param": {}}) 
        all_response["reload_pjsip"] = await execute_ami_command(command_payload)

        command_payload = AMICommandRequest(dc="N",command={"Action": "reload_dialplan","Param": {}}) 
        all_response["reload_dialplan"] = await execute_ami_command(command_payload)

        return {"status": "success", "message": f"Extension {num} successfully modified in Main Exchange configuration context.","response":str(all_response)}    
    except Exception as e:
        return {"status": "error", "message": f"Backend pipeline creation error exception: {str(e)}"}


# --- DELETE EXTENSION ---
@router.post("/extension/delete")
async def delete_existing_extension(payload: ExtensionDeleteRequest):
    try:
        
        numStart = int(payload.numStart)
        numEnd = payload.numEnd
        context = payload.dept.split("-")[0]
        all_response = {}
        if numEnd=="":
            numEnd = numStart
        else:
            numEnd = int(numEnd)
            
        for eachNum in range(numStart,numEnd+1,1):
            
            
            try:
                # Dialplan Delete
                #command_payload.command["Action"] = "delete_dialplan"
                command_payload = AMICommandRequest(
                    dc="N",
                    command={
                        "Action": "get_dialplan",
                        "Param": {
                            "context": context
                            }
                        })
                
                each_response = await execute_ami_command(command_payload)
                match_line = find_extension_line(each_response["output"],eachNum)
                
                if match_line:
                    
                    print("Match Found!!",match_line)
                    # Dialplan Delete by Line in Extension.conf
                    command_payload = AMICommandRequest(
                        dc="N",
                        command={
                            "Action": "delete_dialplan_byline",
                            "Param": {
                                "context": context,
                                "line0": match_line["line0"],
                                "line1": match_line["line1"]
                            }
                        }
                    ) 
                    
                    
                    each_response = await execute_ami_command(command_payload)
                    all_response[eachNum] = each_response["output"]                
                    print("Deleting pjsip_wizard")
                    # Extension Profile Delete by Extension
                    command_payload = AMICommandRequest(
                        dc="N",
                        command={
                            "Action": "delete_extension",
                            "Param": {
                                "context": context,
                                "extension": eachNum
                            }
                        }
                    )
                    
                    each_response = await execute_ami_command(command_payload)
                    all_response[eachNum] = each_response["output"] 
                    
                else:
                    all_response[eachNum] = f"No Matching Extension {eachNum} Found in Context {context}"
            except Exception as e:
                all_response[eachNum] = f"Error Deleting {eachNum}"
                print(f"Error Deleting {eachNum}",str(e))
                
        #print("all_response : ",all_response)
        print("Operation Complete")

                        
        return {"status": "success", "message": f"Extension from {numStart} to {eachNum} successfully deleted in PBX pool configuration context.","response":all_response}      
    except Exception as e:
        return {"status": "error", "message": f"Backend pipeline creation error exception: {str(e)}"}

    
    return command_payload

async def execute_ami_command(payload: AMICommandRequest):
    """
    Executes an ad-hoc custom AMI action payload directly against Asterisk.
    Returns the exact key-value string mapping returned by the core telephony engine.
    """
    try:

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


import re

def find_extension_line(text_data, user_extension):
    # Escape user input to handle any accidental regex special characters safely
    ext = re.escape(str(user_extension))
    
    # Construct the dynamic pattern using an f-string
    # \d{6} matches exactly 6 digits
    # Dial\( handles the literal parenthesis
    pattern = rf"Line-\d{{6}}-(?P<index>\d{{6}})='exten={ext},1,Dial\(PJSIP/{ext}"
    
    # Search the text
    match = re.search(pattern, text_data)
    line0 = match.group("index")
    if match:
        return {
            "full_match": match.group(0),
            "line0": int(line0) ,
            "line1": int(line0)+1
        }
    return None

