# syncCRUD.py
import asyncio
import os



# Path to your sync script
#SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"
SCRIPT_PATH = ""

async def run_asterisk_sync():
    """
    Executes the sync script asynchronously and returns a tuple: (success_boolean, output_message)
    """
    try:
        # Fix potential environment traps (ensures SSH knows where to look for keys)
        env = os.environ.copy()
        if "HOME" not in env:
            #env["HOME"] = config.SERVER_PATH
            env["HOME"] = "/home/exch"

        process = await asyncio.create_subprocess_exec( 
            SCRIPT_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return True, stdout.decode().strip()
        else:
            return False, stderr.decode().strip() or "Unknown script execution error."
            
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("Testing run_asterisk_sync() directly from command line...")
    
    SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"
    
    # Use asyncio.run to execute the async function cleanly
    success, output = asyncio.run(run_asterisk_sync())
    
    print(f"Success Status: {success}")
    print(f"Output:\n{output}")
else:
    # Path to your sync script
    #SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"
    import config
    SCRIPT_PATH = os.path.join(config.SERVER_DIR,"routes/sync_asterisk.sh")