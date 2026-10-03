# amiCommandHelper.py

import json

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
    
#cmd_check = get_ami_command("modify_extension_password",{"extension":"66401","password":"4321"})
#print(cmd_check)

#cmd_check = get_ami_command("reload_pjsip_wizard")
#print(cmd_check)
