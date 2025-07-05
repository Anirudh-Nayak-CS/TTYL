# server.py
import socket
import threading

# --- Config ---
HOST = '0.0.0.0'
PORT = 5555

# --- Setup ---
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

def broadcast(message, _client):
    for client in clients:
        if client != _client:
            client.send(message)

def handle_client(client):
    while True:
        try:
            msg = client.recv(1024)
            broadcast(msg, client)
        except:
            clients.remove(client)
            client.close()
            break

def receive():
    print(f"Server started on port {PORT}")
    while True:
        client, addr = server.accept()
        print(f"Connected with {addr}")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive()
