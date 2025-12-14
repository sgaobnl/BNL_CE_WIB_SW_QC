import subprocess

def ping_host(ip_address="192.168.121.1", count=4):
    """
    Pings the specified IP address on Windows.

    Args:
        ip_address (str): The IP address to ping.
        count (int): Number of ping attempts.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    try:
        # Use Windows ping command: -n <count> specifies the number of pings
        result = subprocess.run(
            ["ping", "-n", str(count), ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stdout)  # Print ping results

        return "Reply from" in result.stdout  # True if host responds, False otherwise

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if ping_host():
        print("Host is reachable!")
    else:
        print("Host is unreachable!")