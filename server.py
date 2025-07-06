import socket
import threading

# --- Config ---
HOST = '0.0.0.0'
PORT = 5555
PVT_MSG="/msg"
REQ_USERNAMES = ["/usernames", "/username"]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}

def broadcast(message, sender_client):
    for client in clients:
        if client != sender_client:
            client.send(message.encode('utf-8'))

def privatemsg(message, sender_client, receiver_client):
    for client in clients:
        if(client==receiver_client):
            msg=f"[PRIVATE MESSAGE FROM {usernames[sender_client]}]:{message}"
            client.send(msg.encode('utf-8'))

def requsername(req_client):
    msg=""
    for client in clients:
        msg+=f"{usernames[client]} "
    req_client.send(msg.encode('utf-8'))

def handle_client(client):
    try:
        # Receive and store the username
        username = client.recv(1024).decode('utf-8')
        usernames[client] = username
        print(f"[+] {username} connected.")
        clients.append(client)

        # Notify others
        broadcast(f"🟢 {username} joined the chat!", client)

        # Handle messages
        while True:
            msg = client.recv(1024)
            msg_decoded=msg.decode('utf-8')
            if not msg:
                break
            print(f"[SERVER:LOG] [{username}]: {msg_decoded}")
            if msg_decoded.startswith(PVT_MSG):
                content = msg_decoded[len(PVT_MSG):].strip()
                try:
                    receiver_username, message = content.split(' ', 1)  #Old Mistake: was sending receiver_username, but have to send receiver_client
                    receiver_client = None
                    for sock, uname in usernames.items():
                        if uname == receiver_username:
                            receiver_client = sock
                            break

                    if receiver_client:
                        privatemsg(message, client, receiver_client)
                    else:
                        client.send(f"[SERVER]: User '{receiver_username}' not found.".encode('utf-8'))
                except ValueError:
                    client.send("[SERVER]: Invalid private message format. Use /msg username message".encode('utf-8'))
                continue

            if msg_decoded in REQ_USERNAMES:
                requsername(client)
                continue


            broadcast(f"[{username}]: {msg_decoded}", client)
            

    except:
        pass
    finally:
        # Clean up
        if client in clients:
            clients.remove(client)
            broadcast(f"🔴 {usernames[client]} left the chat.", client)
            print(f"[-] {usernames[client]} disconnected.")
            del usernames[client]
        client.close()

def receive():
    print(f"Server started on port {PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

receive()
