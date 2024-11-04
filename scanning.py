import asyncio
import socket
import threading
from bleak import BleakScanner
from datetime import datetime

# Global connection variable for socket
conn = None
lock = threading.Lock()

# Load authorized MAC addresses for comparison
def load_authorized_macs(file_path='authorized_macs.txt'):
    authorized_users = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    mac, name = parts[0].strip(), parts[1].strip()
                    authorized_users[mac] = name
                    print(f"Loaded authorized MAC: {mac}, Name: {name}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    return authorized_users

# Bluetooth scanning function
async def scan_bluetooth_devices():
    print("Starting Bluetooth scan...")
    authorized_users = load_authorized_macs()
    while True:  # Continuous scanning
        devices = await BleakScanner.discover(timeout=30)
        print(f"Scanning completed at {datetime.now()}")

        for device in devices:
            device_name = device.name or 'Unknown'
            device_mac = device.address
            print(f"Device: {device_name} | MAC: {device_mac}")

            # Check if the device MAC address is in the authorized list
            if device_mac in authorized_users:
                user_name = authorized_users[device_mac]
                welcome_message = f"Welcome {user_name} (MAC: {device_mac})"
                print(welcome_message)

                # Send welcome message with the MAC address to C# client
                send_message(welcome_message)

        await asyncio.sleep(40)  # Delay before next scan

# Function to send a message to the C# client
def send_message(message):
    with lock:  # Ensure thread safety
        if conn:
            conn.sendall(message.encode())


# Socket communication function
def start_socket_server():
    global conn
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind(('localhost', 5000))
    mySocket.listen(1)

    print("Waiting for C# client to connect...")
    conn, addr = mySocket.accept()
    print("Client connected from:", addr)

    # Start Bluetooth scanning in the main socket thread
    asyncio.run(scan_bluetooth_devices())

# Run the socket server in a thread
socket_thread = threading.Thread(target=start_socket_server)
socket_thread.start()

# Wait for the socket server to complete
socket_thread.join()
print("Bluetooth scanner and socket server are running.")
