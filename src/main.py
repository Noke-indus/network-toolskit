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

def get_Network_info():
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

def get_wifi_info(interface):
    output = run_command(["iw","dev",interface,"link"])
    if not output or "Not connected" in output:
        return None
    wifi = {}
    ssid = re.search(r"SSID:\s+(.+)",output)
    signal = re.search(r"signal:\s+(-?\d+)\s+dBm",output)
    tx_rate = re.search(r"tx bitrate:\s+(.+)",output)

    if ssid:
        wifi["SSID"] = ssid.group(1)
    if signal:
        wifi["Signal"] = signal.group(1)
    if tx_rate:
        wifi["TX Rate"] = tx_rate.group(1)

    return wifi

def ping_test(host):
    result = subprocess.run(["ping","-c","1","-W","2",host],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return result.returncode == 0

def dns_test():
    try:
        socket.gethostbyname("example.com")
        return True
    except socket.gaierror:
        return False

def main():
    print("="*45)
    print("     uConsole Network Toolkit v0.1")
    print("="*45)

    interface, ip_address, gateway=(get_Network_info())

    print()

    print(f"Hostname    :{socket.gethostname()}")
    print(f"Interface   :{interface}")
    print(f"IPv4        :{ip_address}")
    print(f"Gateway     :{gateway}")

    dns_servers = get_dns_servers()
    
    if  dns_servers:
        print(f"DNS         :{','.join(dns_servers)}")
    else:
        print("DNS          ：Unknown")

    wifi = get_wifi_info(interface)

    if wifi:
        print()
        print("[Wi-Fi]")

        for key, value in wifi.items():

            print(f"{key:<10}:{value}")
    print()
    print("[Connectivity]")

    gateway_ok = False

    if gateway != "Unknown":
        gateway_ok=ping_test(gateway)
    interface_ok = ping_test("1.1.1.1")

    dns_ok = dns_test()
    internet_ok = ping_test("1.1.1.1")

    print(f"Gateway    : "f"{'OK' if gateway_ok else 'FAIL'}")
    print(f"Internet   : "f"{'OK' if internet_ok else 'FAIL'}")
    print(f"DNS        : "f"{'OK' if dns_ok else 'FAIL'}")

    print()
    print("[Diagnosis]")

    if not gateway_ok:
        print("Cannot reach local gateway")
    elif not interface_ok:
        print("LAN works, but Internet access failed.")
    elif not dns_ok:
        print("Internet works, but DNS resolution failed.")
    else:
        print("Network connection looks healthy.")

    print("="*45)

if __name__ == "__main__": main()