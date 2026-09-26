import subprocess
import socket
import re
from pathlib import Path

def run_command(command):
    try:
        result = subprocess.run(command,capture_output=True,text=True,timeout=5)
        return result.stdout.strip()
    except Exception as error:
        return "Command Error:"+{error}

def get_work_info():
    route = run_command(["ip","route","get","1.1.1.1"])

    interface = "Unknown"
    ip_address = "Unkonwn"

    interface_match = re.search(r"dev\s+(\S+)",route)
    ip_match = re.search(r"src\s+(\S+)",route)

    if interface_match:
        interface = interface_match.group(1)
    
    if ip_match:
        ip_address = ip_match.group(1)
        default_route = run_command(["ip","route","show","default"])
        gateway = "Unkonwn"
        gateway_match = re.search(r"default via\s+(\S+)",default_route)
    
    if gateway_match:
        gateway = gateway_match.group(1)
        
    return interface,ip_address,gateway

def get_dns_servers():
    path = Path("/etc/resolv.conf")

    if not path.exists():
        return []

    dns_servers = []

    for line in path.read_text().splitlines(): 

        line = line.strip()

        if line.startswith("nameserver"):
            parts = line.split()

            if len(parts) >= 2:
                dns_servers.append(parts[1])

    return dns_servers



def show_dns_servers():
    dns_servers = get_dns_servers()
    if not dns_servers:
        print("No DNS servers found")
    else:
        print(dns_servers)