import socket
import struct

def send_tcp_command(ip="192.168.121.1", port=22):
    """
    Sends a properly formatted command [key=DEADBEEF cmd=E AUX=0 Addr=0 Data=0]
    to the TCP server.
    """
    try:
        # Define command values
        SYSKEY = 0xDEADBEEF  # Fixed system key
        CMD    = 0x0000      # Command 0xE (14 in decimal)
        AUX    = 0x0000      # Auxiliary value
        ADDR   = 0x00000000  # Address
        DATA   = 0x00000000  # Data

        # Pack data into a 16-byte binary format (big-endian)
        message = struct.pack(">IHHII", SYSKEY, CMD, AUX, ADDR, DATA)

        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set timeout

        # Connect to the server
        print(f"Connecting to {ip}:{port}...")
        sock.connect((ip, port))
        print("Connected!")

        # Send the binary message
        sock.sendall(message)
        print(f"Sent: {message.hex().upper()}")  # Print the raw hex data sent

        # Receive response (expecting 4-byte response)
        response = sock.recv(4)
        if response:
            response_data = struct.unpack(">I", response)[0]  # Unpack as 4-byte integer
            print(f"Response from server: 0x{response_data:08X}")

        # Close the socket
        sock.close()

    except Exception as e:
        print(f"Error: {e}")

# ✅ Send the test command
send_tcp_command()
