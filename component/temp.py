import socket
import time

SERVER_IP = "192.168.121.1"
PORT = 23  # Change if necessary (23 for Telnet, 22 for SSH)
USERNAME = "root"
PASSWORD = "root"
INITIAL_COMMAND = "source ./FEMB_start"

def receive_response(sock):
    """ Helper function to receive data from the socket """
    time.sleep(0.5)  # Reduced from 1s to 0.5s
    response = sock.recv(4096).decode(errors='ignore')
    print(response)  # Print the response for debugging
    return response

def connect_to_server():
    """ Establishes connection to the Zynq server and logs in """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        print("Connected to server.")

        # Read initial login prompt
        receive_response(s)

        # Send username and read response
        s.sendall((USERNAME + "\n").encode())
        receive_response(s)

        # Send password and read response
        s.sendall((PASSWORD + "\n").encode())
        receive_response(s)

        # Ensure login completion
        s.sendall(b"\n")
        receive_response(s)

        print("Login successful.")
        return s  # Keep the socket open for further commands

    except Exception as e:
        print("Connection error:", e)
        return None

def send_command(sock, command, wait_for_prompt=True):
    """ Sends a command to the server and receives the response """
    try:
        sock.sendall((command + "\n").encode())
        response = receive_response(sock)

        # If command runs in background (&), send another newline to get prompt back
        if wait_for_prompt and '&' in command:
            time.sleep(1)
            sock.sendall(b"\n")
            receive_response(sock)

        return response
    except Exception as e:
        print("Error sending command:", e)
        return None

def start_femb_service_background(sock):
    """ Start FEMB service and put it in background (simulate Ctrl+Z then bg) """
    try:
        print("Starting FEMB service...")

        # Send the source command
        sock.sendall((INITIAL_COMMAND + "\n").encode())

        # Wait for service to start (look for "started server" message)
        time.sleep(2)  # Reduced from 3s to 2s

        # Read initial output
        try:
            sock.settimeout(2)
            output = sock.recv(4096).decode(errors='ignore')
            print("Service startup output:", output[:200])  # Print first 200 chars
        except:
            pass
        sock.settimeout(None)

        # Send Ctrl+Z (ASCII 26) to suspend the process
        print("Suspending process with Ctrl+Z...")
        sock.sendall(b"\x1a")  # Ctrl+Z
        time.sleep(0.5)  # Reduced from 1s to 0.5s

        # Receive response
        try:
            sock.settimeout(2)
            response = sock.recv(4096).decode(errors='ignore')
            print("Suspend response:", response[:200])
        except:
            pass
        sock.settimeout(None)

        # Send 'bg' command to put job in background
        print("Putting job in background with 'bg' command...")
        sock.sendall(b"bg\n")
        time.sleep(0.5)  # Reduced from 1s to 0.5s

        # Get prompt back
        try:
            sock.settimeout(2)
            response = sock.recv(4096).decode(errors='ignore')
            print("Background response:", response[:200])
        except:
            pass
        sock.settimeout(None)

        # Send newline to get clean prompt
        sock.sendall(b"\n")
        time.sleep(0.5)

        print("FEMB service started in background")
        return True

    except Exception as e:
        print(f"Error starting FEMB service in background: {e}")
        return False

def disconnect():
    """ Closes the Telnet connection """
    global connection
    if connection:
        try:
            connection.close()
            print("Telnet connection closed.")
            connection = None
        except Exception as e:
            print(f"Error closing connection: {e}")

def check_wib_service_healthy():
    """ Check if WIB service is healthy and responding correctly """
    import socket
    import struct
    try:
        # Connect to WIB TCP port
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(3)
        test_sock.connect((SERVER_IP, 32010))

        # Send a simple version query command (same as wib_ver)
        SYSKEY = 0xdeadbeef
        cmd = 0x0
        SYSKEY_B = SYSKEY.to_bytes(4, byteorder='big')
        cmd_B = cmd.to_bytes(2, byteorder='big')
        aux_B = (0).to_bytes(2, byteorder='big')
        addr_B = (0).to_bytes(4, byteorder='big')
        data_B = (0).to_bytes(4, byteorder='big')
        msg = SYSKEY_B + cmd_B + aux_B + addr_B + data_B

        test_sock.sendall(msg)
        response = test_sock.recv(4096)
        test_sock.close()

        # If we got a response, service is healthy
        return len(response) > 0
    except:
        return False

def restart_wib_service(force=False, max_retries=3, retry_delay=5):
    """ Restart WIB service by killing old process and running FEMB_start

    Args:
        force: Force restart even if service appears healthy
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Seconds to wait between retries (default: 5)

    Returns:
        True if service started successfully, False otherwise
    """
    global connection

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\033[33m" + f"Retry attempt {attempt}/{max_retries-1}..." + "\033[0m")
            time.sleep(retry_delay)

        # Close existing connection if any
        if connection:
            try:
                connection.close()
                print("Closed existing Telnet connection")
            except:
                pass
            connection = None

        print("=" * 60)
        print(f"Restarting WIB service... (attempt {attempt + 1}/{max_retries})")
        print("=" * 60)

        conn = connect_to_server()
        if conn:
            # Kill any existing WIB server processes
            print("Killing old WIB processes...")
            send_command(conn, "killall -9 wib_server 2>/dev/null")
            send_command(conn, "killall -9 wr_nic_daemon 2>/dev/null")
            # Find and kill processes using port 32010
            send_command(conn, "fuser -k 32010/tcp 2>/dev/null")
            time.sleep(1)

            # Restart the service using background method
            print("Starting FEMB_start...")
            if not start_femb_service_background(conn):
                print("Failed to start service, trying simple method...")
                send_command(conn, INITIAL_COMMAND + " &")
                time.sleep(5)

            # Verify service is now responding
            if check_wib_service_healthy():
                print("\033[32m" + "✓ WIB service restart successful and verified" + "\033[0m")
                connection = conn
                return True
            else:
                print("\033[31m" + "✗ WARNING: WIB service restarted but not responding properly" + "\033[0m")
                try:
                    conn.close()
                except:
                    pass
                connection = None
                # Continue to next retry attempt
        else:
            print("\033[31m" + "Failed to connect to server" + "\033[0m")

    print("\033[31m" + f"Service restart failed after {max_retries} attempts" + "\033[0m")
    return False


def restart_wib_service_with_full_test_retry(test_func, max_test_retries=3, *args, **kwargs):
    """
    Wrapper to run a test function with automatic retry on connection failures.

    This function monitors for connection errors during test execution and
    automatically restarts the entire test if connection failures are detected.

    Args:
        test_func: The test function to run
        max_test_retries: Maximum number of times to retry the entire test
        *args, **kwargs: Arguments to pass to the test function

    Returns:
        The result of test_func if successful, None if all retries failed
    """
    for attempt in range(max_test_retries):
        if attempt > 0:
            print("\033[33m" + "=" * 60 + "\033[0m")
            print(f"\033[33mRestarting entire test (attempt {attempt + 1}/{max_test_retries})...\033[0m")
            print("\033[33m" + "=" * 60 + "\033[0m")
            # Force a clean service restart before retrying
            restart_wib_service(force=True, max_retries=5, retry_delay=5)

        try:
            result = test_func(*args, **kwargs)
            return result
        except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
            error_str = str(e)
            if "Connection refused" in error_str or "Errno 111" in error_str or \
               "Transport endpoint is not connected" in error_str or "Errno 107" in error_str:
                print(f"\033[31mConnection error detected: {e}\033[0m")
                print(f"\033[33mWill retry test from beginning...\033[0m")
                continue
            else:
                raise
        except Exception as e:
            error_str = str(e)
            # Check if it's a connection-related error
            if "Connection refused" in error_str or "Errno 111" in error_str or \
               "Transport endpoint is not connected" in error_str or "Errno 107" in error_str:
                print(f"\033[31mConnection error detected: {e}\033[0m")
                print(f"\033[33mWill retry test from beginning...\033[0m")
                continue
            else:
                raise

    print(f"\033[31mTest failed after {max_test_retries} attempts\033[0m")
    return None


def ensure_wib_service_healthy(max_retries=5, retry_delay=5):
    """
    Ensure WIB service is healthy, with automatic restart and retry if not.

    This function should be called before critical operations to ensure
    the WIB service is ready.

    Args:
        max_retries: Maximum number of restart attempts
        retry_delay: Seconds to wait between attempts

    Returns:
        True if service is healthy, False if all attempts failed
    """
    # First check if already healthy
    if check_wib_service_healthy():
        return True

    print("\033[33mWIB service not healthy, attempting restart...\033[0m")
    return restart_wib_service(force=True, max_retries=max_retries, retry_delay=retry_delay)

# if __name__ == "__main__":
# Initialize connection (will be used to start service if needed)
connection = None

# Try to check if service is already running
try:
    if check_wib_service_healthy():
        print("WIB service is already running and healthy - skipping initialization")
    else:
        print("WIB service not detected - starting service...")
        restart_wib_service()
except Exception as e:
    print(f"Could not check service status, attempting to start: {e}")
    conn = connect_to_server()
    if conn:
        if not start_femb_service_background(conn):
            print("Background start failed, trying simple method...")
            send_command(conn, INITIAL_COMMAND + " &")
        time.sleep(3)
        connection = conn

        # Allow user to send further commands
        # while True:
        #     cmd = input("Enter command to send (or 'exit' to close): ")
        #     if cmd.lower() == "exit":
        #         print("Closing connection...")
        #         connection.close()
        #         break
        #     else:
        #         send_command(connection, cmd)


