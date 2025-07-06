import socket
import threading

# --- Configuration ---
SERVER_IP = '127.0.0.1'  # Change to your server's IP
SERVER_PORT = 5555       # Must match server's port
DISCONNECT_MESSAGE="/quit"



client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

username = input("Enter your username: ")
client.send(username.encode('utf-8'))

print("Connected to server. You can start chatting!\n")

# --- Receive messages from server ---
def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(f"\n{message}")
            else:
                print("\nDisconnected from server.")
                break
        except:
            print("\nError receiving message.")
            break

# --- Send messages to server ---
def send_messages():
    while True:
        message = input()
        if message== DISCONNECT_MESSAGE:
            client.close()
            break
        try:
            client.send(message.encode('utf-8'))
        except:
            print("Failed to send message.")
            break

# --- Run threads for sending and receiving ---
recv_thread = threading.Thread(target=receive_messages)
recv_thread.daemon = True
recv_thread.start()

send_messages()  # Runs on main thread
