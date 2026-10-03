

# routes/telephony.py

import asyncio
from fastapi import APIRouter
from asterisk_worker import ami_manager, ALL_EXTENSIONS

router = APIRouter()

@router.get("/extensions-data")
async def get_all_extensions_data():
    """
    Returns the real-time parsed extensions data array.
    Responds instantly because it evaluates our background memory cache cache.
    """
    # 1. First, parse static configuration parameters (CallerID & Context) out of the wizard file
    config_map = {}
    
    try:
        wizard_config = await ami_manager.send_action({'Action': 'GetConfig', 'Filename': 'pjsip_wizard.conf'})
        #print("wizard_config : ",type(wizard_config),wizard_config)
        if hasattr(wizard_config, 'headers'):
            headers = wizard_config.headers
            category_count = 0
            
            while f"category-{category_count:06d}" in headers:
                ext_num = headers[f"category-{category_count:06d}"]
                
                line_index = 0
                assigned_callerid = f"Extension {ext_num}"
                assigned_context = "from-internal"
                
                while f"line-{category_count:06d}-{line_index}" in headers:
                    line_data = headers[f"line-{category_count:06d}-{line_index}"]
                    if "=" in line_data:
                        var_name, var_value = line_data.split("=", 1)
                        var_name, var_value = var_name.strip(), var_value.strip()
                        if var_name == "endpoint/callerid":
                            assigned_callerid = var_value
                        elif var_name == "endpoint/context":
                            assigned_context = var_value
                    line_index += 1
                
                config_map[ext_num] = {
                    "callerid": assigned_callerid,
                    "context": assigned_context
                }
                category_count += 1
    except Exception as e:
        print(f"pjsip_wizard.conf file parsing skipped or unavailable: {e}")

    print("config_map : ",config_map)
    #2 get all endpoint
    
    local_accumulator = {}
    print("Fetching active extension roster straight from the Asterisk AMI socket...")
    try:

        pjsip_responses = await ami_manager.send_action({'Action': 'PJSIPShowEndpoints'}, as_list=True)

        # Verify the returned object structure is a valid unpacked list sequence
        if isinstance(pjsip_responses, list):
            for response in pjsip_responses:
                ext_num = response.get('objectname', '')
                # Ignore global system templates or null entries
                if ext_num and ext_num != 'unknown':
                    dev_state = response.get('devicestate', '').lower()
                    local_accumulator[ext_num] = {
                        "num": ext_num,
                        "name": config_map[ext_num].get("callerid","NA") if ext_num in config_map else "NA",
                        "context": config_map[ext_num].get("context","NA") if ext_num in config_map else "NA",
                        "Contacts": response.get('contacts'),
                        "is_registered": dev_state.lower() not in ['unavailable', 'unknown', 'invalid']
                    }
                    
    except Exception as e:
        print(f"PJSIP inventory query bypassed: {e}")
        
    ALL_EXTENSIONS = local_accumulator

    # Convert the running cache into a clean sorted array
    return sorted(list(ALL_EXTENSIONS.values()), key=lambda x: x['num'])


@router.get("/extensions-data-old")
async def get_all_extensions_data():
    """
    Fetches extension records straight from Asterisk AMI using standard promise unpacking.
    Ensures zero thread locks and handles non-iterable future object blocks safely.
    """
    local_accumulator = {}

    print("Fetching active extension roster straight from the Asterisk AMI socket...")
    try:
        # 1. Instruct panoramisk to package multi-line responses into a list using as_list=True
        # We await the complete Future response array sequence directly
        pjsip_responses = await ami_manager.send_action({'Action': 'PJSIPShowEndpoints'}, as_list=True)
        
        # Verify the returned object structure is a valid unpacked list sequence
        if isinstance(pjsip_responses, list):
            for response in pjsip_responses:
                ext_num = response.get('objectname', '')
                # Ignore global system templates or null entries
                if ext_num and ext_num != 'unknown':
                    dev_state = response.get('devicestate', '').lower()
                    local_accumulator[ext_num] = {
                        "num": ext_num,
                        "name": response.get('description') or f"Extension {ext_num}",
                        "dept": "Internal PBX",
                        "is_registered": dev_state not in ['unavailable', 'unknown', 'invalid']
                    }
    except Exception as e:
        print(f"PJSIP inventory query bypassed: {e}")

    # 3. Development Fallback Matrix: If your sandbox testing environment 
    # has no physical lines configured, serve data so your layout handles render
    if not local_accumulator:
        print("Asterisk returned zero records.")
        return [
            {"num": "1", "name": "Aditya", "dept": "Admin", "is_registered": True}
        ]

    # Return clean sorted json collection rows straight to your frontend fetch script
    return sorted(list(local_accumulator.values()), key=lambda x: x['num'])
