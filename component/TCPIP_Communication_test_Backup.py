import subprocess
import re


def get_adapter_name(ip_address):
    """Finds the network adapter name associated with a specific IP address."""
    command = "wmic nicconfig where IPEnabled=True get Description,IPAddress"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    for line in result.stdout.split("\n"):
        if ip_address in line:
            match = re.search(r'(.+?)\s+\[', line)
            if match:
                return match.group(1).strip()
    return None


def change_ip(adapter_name, new_ip, subnet_mask):
    """Changes the IP address and subnet mask for the given adapter."""
    command = f'netsh interface ip set address name="{adapter_name}" static {new_ip} {subnet_mask}'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Successfully changed IP to {new_ip} on {adapter_name}")
    else:
        print(f"Failed to change IP: {result.stderr}")


# Step 1: Get Adapter Name
target_ip = "192.168.121.1"
adapter_name = get_adapter_name(target_ip)

if adapter_name:
    print(f"Found adapter: {adapter_name}")

    # Step 2: Change IP Address
    new_ip = "192.168.121.12"
    subnet_mask = "255.255.255.0"
    change_ip(adapter_name, new_ip, subnet_mask)
else:
    print(f"No adapter found with IP {target_ip}")
