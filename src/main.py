import subprocess
import socket
import re
from pathlib import Path

def run_command(command):
    try:
        result = subprocess.run(command,capture_output=True,text=True,timeout=5)
        return result.stdout.strip()
    except Exception as error:
        return {error}
def get_work_info():
	route = run_command(["ip","route","get","1.1.1.1"])
	interface = "Unknown"
	ip_address = "Unkonwn"

	interface_match = re.search(r"dev\s+(\S+)",route)
