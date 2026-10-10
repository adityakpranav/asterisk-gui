# syncCRUD.py
import asyncio
import os

# Path to your sync script
SCRIPT_PATH = "/home/exch/asteriskGUI/routes/sync_asterisk.sh"


async def run_asterisk_sync():
    """
    Executes the sync script asynchronously and returns a tuple: (success_boolean, output_message)
    """
    try:
        # Fix potential environment traps (ensures SSH knows where to look for keys)
        env = os.environ.copy()
        if "HOME" not in env:
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
