# syncCRUD.py
import asyncio
import os
import subprocess



# Path to your sync script
#SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"

keepalived_SCRIPT_PATH = ""
asterisk_SCRIPT_PATH = ""
log_SCRIPT_PATH = ""

def run_script(SCRIPT_PATH,*args):
    res = subprocess.run(
        ["bash", SCRIPT_PATH,*args],
        capture_output=True,
        text=True
    )
    #return {"is_active": res.returncode == 0,"output": res.stdout.strip(),"error": res.stderr.strip()}
    #print("res : ",str(res))
    return res.returncode == 0, res.stdout.strip()

async def asterisk_restart():
    # Method to run fixed script
    success, output = run_script(asterisk_SCRIPT_PATH,"restart")
    return success, output

async def asterisk_status():
    # Method to run fixed script
    success, output = run_script(asterisk_SCRIPT_PATH,"status")
    return (success, output)

async def keepalive_restart():
    # Method to run fixed script
    success, output = run_script(keepalived_SCRIPT_PATH,"restart")
    return success, output


async def keepalive_status():
    # Method to run fixed script
    success, output = run_script(keepalived_SCRIPT_PATH,"status")
    return (success, output)

async def app_logs(Service, Option, Value):
    # Method to run fixed script
    success, output = run_script(log_SCRIPT_PATH, Service, Option, Value)
    return (success, output)



if __name__ == "__main__":
    
    print("Testing directly from command line...")
    
    asterisk_SCRIPT_PATH = "/home/exch2/asteriskGUI/routes/scripts/script_asterisk.sh"
    keepalived_SCRIPT_PATH = "/home/exch2/asteriskGUI/routes/scripts/script_keepalived.sh"
    log_SCRIPT_PATH = "/home/exch2/asteriskGUI/routes/scripts/script_logs.sh"

    # Use asyncio.run to execute the async function cleanly
    #success, output = asterisk_status()
    success, output = asterisk_restart()
    
    print(f"Success Status: {success}")
    print(f"Output:\n{output}")
else:
    # Path to your sync script
    #SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"
    import config
    asterisk_SCRIPT_PATH = os.path.join(config.SERVER_DIR,"asteriskGUI/routes/scripts/script_asterisk.sh")
    keepalived_SCRIPT_PATH = os.path.join(config.SERVER_DIR,"asteriskGUI/routes/scripts/script_keepalived.sh")
    log_SCRIPT_PATH = os.path.join(config.SERVER_DIR,"asteriskGUI/routes/scripts/script_logs.sh")