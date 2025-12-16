import subprocess
import platform


def ping_host(ip_address="192.168.121.1", count=4):
    """
    Pings the specified IP address on Windows or Linux/Ubuntu.
    Automatically detects the operating system and uses appropriate command.

    Args:
        ip_address (str): The IP address to ping.
        count (int): Number of ping attempts.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    try:
        # Detect the operating system
        system = platform.system().lower()

        if system == "windows":
            # Windows ping command: -n <count>
            cmd = ["ping", "-n", str(count), ip_address]
            success_indicator = "Reply from"
        else:
            # Linux/Unix/Mac ping command: -c <count> -W <timeout>
            cmd = ["ping", "-c", str(count), "-W", "1", ip_address]
            success_indicator = None  # Use return code instead

        print(f"Detected OS: {platform.system()}")
        print(f"Pinging {ip_address}...\n")

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stdout)  # Print ping results

        # Determine success based on OS
        if system == "windows":
            return success_indicator in result.stdout
        else:
            return result.returncode == 0

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    if ping_host():
        print("\n✓ Host is reachable!")
    else:
        print("\n✗ Host is unreachable!")