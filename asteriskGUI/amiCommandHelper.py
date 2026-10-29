# amiCommandHelper.py

import json
from schemas import AMICommandRequest
from asterisk_worker import ami_manager

# 2. Reusable helper function to inject variables and format the dictionary
def get_ami_command(template_name,kwargs=None):
    
    # 1. Load your templates safely into memory
    with open("ami_templates.json", "r") as f:
        ami_templates = json.load(f)
    
    # Replace all placeholders with your active variables
    if kwargs:
        template_str = ami_templates[template_name]
        #template_str = template_str.format(**kwargs)
            # 2. Iterate over the keys/values and replace text safely
        formatted_cmd = {}
        for key, value in template_str.items():
            # Check if the value is a string and contains placeholders
            if isinstance(value, str):
                formatted_cmd[key] = value.format(**kwargs)
            else:
                formatted_cmd[key] = value
        return formatted_cmd
    else:
        # Convert it back to a clean Python dictionary for Panoramisk
        template_str = json.dumps(ami_templates[template_name])
        return json.loads(template_str)


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
        #print("response detail : ",type(response),len(response))
        #print("response : ",response)

        try:
            #return {"status": "success", "output": json.dumps(response.as_dict())}
            return {"status": "success", "raw_output": response, "output":str(response)}
        except Exception as e:
            print("Error execute_ami_command parsing to json", str(e))
            return {"status": "success", "output": str(response)}
            
    except Exception as e:
         
        return {"status": "error", "output": f"Execution Error Exception Raised:\n{str(e)}"}


#cmd_check = get_ami_command("modify_extension_password",{"extension":"66401","password":"4321"})
#print(cmd_check)

#cmd_check = get_ami_command("reload_pjsip_wizard")
#print(cmd_check)
