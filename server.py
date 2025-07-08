import socket
import threading

HEADER=1024
PORT=5050
FORMAT="utf-8"
DISCONNECT_MESSAGE="/quit"
WELCOME_MESSAGE = (
    "╔════════════════════════════════════════════════╗\n"
    "║                Welcome to TTYL                 ║\n"
    "╠════════════════════════════════════════════════╣\n"
    "║ Commands:                                      ║\n"
    "║ /quit               → Disconnect from server   ║\n"
    "║ /msg <username> msg → Privately message a user ║\n"
    "║ /users              → List of users online     ║\n"
    "║ /kick <username>    → Kick a user              ║\n"
    "║ /ban <username>     → Ban a user               ║\n"  
    "╚════════════════════════════════════════════════╝"

)


clients={}
admins=[]
banned_usernames=[]

SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(ADDR)


def broadcast(message,currclientusername):
  final_message=message.encode(FORMAT)
  final_message_length=len(final_message)
  final_message_length=str(final_message_length).encode(FORMAT)
  final_message_length+=b' '*(HEADER-len(final_message_length))
  for username,conn in clients.items():
    if username!=currclientusername:
       
       conn.send(final_message_length)
       conn.send(final_message)



def listallusers(conn):
  online_users=', '.join(clients.keys())
  final_message=f"{online_users}".encode(FORMAT)
  final_message_length=len(final_message)
  final_message_length=str(final_message_length).encode(FORMAT)
  final_message_length+=b' '*(HEADER-len(final_message_length))
  conn.send(final_message_length)
  conn.send(final_message)



def msgPrivately(message,currclientusername):
  msg_parts=message.split(' ',2)
  
  connection_sender=clients[currclientusername]
  if len(msg_parts)<3:
    connection_sender.send("[SERVER] Invalid format.Use /msg <username> msg".encode(FORMAT))
    return
  
  user=msg_parts[1]
  actualmessage=msg_parts[2]
  if user not in clients:
    connection_sender.send("[SERVER] User is not online".encode(FORMAT))
  else:  
   connection_receiver=clients[user]
   final_message=f"[Private message from {currclientusername}] {actualmessage}".encode(FORMAT)
   final_message_length=len(final_message)
   final_message_length=str(final_message_length).encode(FORMAT)
   final_message_length+=b' '*(HEADER-len(final_message_length))
   connection_receiver.send(final_message_length)
   connection_receiver.send(final_message) 
   
   
   confirmation_message=f"Your message was sent to {user} successfully".encode(FORMAT)
   confirmation_message_length=len(confirmation_message)
   confirmation_message_length=str(confirmation_message_length).encode(FORMAT)
   confirmation_message_length+=b' '*(HEADER-len(confirmation_message_length))  
   connection_sender.send(confirmation_message_length)
   connection_sender.send(confirmation_message)

def handleKick(msg):
  msg_parts=msg.split(' ')
  if len(msg_parts)<2:
    return
  username=msg_parts[1]
  if username!="admin" and username in clients:
    kick_user_conn=clients[username]
    del clients[username]
    message="You were kicked by an admin."
    final_message=message.encode(FORMAT)
    final_message_length=len(final_message)
    final_message_length=str(final_message_length).encode(FORMAT)
    final_message_length+=b' '*(HEADER-len(final_message_length))   
    kick_user_conn.send(final_message_length)
    kick_user_conn.send(final_message)
    kick_broadcast_msg=f"👢 {username} was kicked from the server."
    broadcast(kick_broadcast_msg,username)  
    kick_user_conn.close()
    return  

def handleBan(msg):
  msg_parts=msg.split(' ')
  if len(msg_parts)<2:
    return
  username=msg_parts[1]
  if username!="admin" and username in clients:
    ban_user_conn=clients[username]
    banned_usernames.append(username)
    del clients[username]
    message="You were banned by an admin."
    final_message=message.encode(FORMAT)
    final_message_length=len(final_message)
    final_message_length=str(final_message_length).encode(FORMAT)
    final_message_length+=b' '*(HEADER-len(final_message_length))   
    ban_user_conn.send(final_message_length)
    ban_user_conn.send(final_message)
    ban_broadcast_msg=f"🔨 {username} was banned from the server."
    broadcast(ban_broadcast_msg,username)  
    ban_user_conn.close()
    return

def handleClient(conn,addr):

  connected=True
  while connected:
    while True:
     username_length=conn.recv(HEADER).decode(FORMAT)

     if username_length:
      username_length=int(username_length)
      username=conn.recv(username_length).decode(FORMAT)
       
      if username in banned_usernames:
        message="You are banned from the server."
        final_message=message.encode(FORMAT)
        final_message_length=len(final_message)
        final_message_length=str(final_message_length).encode(FORMAT)
        final_message_length+=b' '*(HEADER-len(final_message_length))   
        conn.send(final_message_length)
        conn.send(final_message)
        conn.close()
        return

      elif username=="admin": 
        rawdata=conn.recv(HEADER)       
       
        if not rawdata:
         connected=False
         if username in clients:
             del clients[username]
         if conn in admins:
            admins.remove(conn)  
         print(f"[Client {username}] disconnected")
         broadcast(f" 🔴 {username} left the chat. ",username)
         break
        password_length=int(rawdata.decode(FORMAT))
        password=conn.recv(password_length).decode(FORMAT)
         
        if password=="notanadminpassword":
          message="Welcome Admin!"
          final_message=message.encode(FORMAT)
          final_message_length=len(final_message)
          final_message_length=str(final_message_length).encode(FORMAT)
          final_message_length+=b' '*(HEADER-len(final_message_length))   
          conn.send(final_message_length)
          conn.send(final_message) 
          clients["admin"] = conn 
          admins.append(conn)
          break

        else :
         message="Wrong password"
         final_message=message.encode(FORMAT)
         final_message_length=len(final_message)
         final_message_length=str(final_message_length).encode(FORMAT)
         final_message_length+=b' '*(HEADER-len(final_message_length))   
         conn.send(final_message_length)
         conn.send(final_message) 

         conn.close()
         return 

      elif username in clients:
       message="[SERVER] Username already exists. Please enter another username."
       final_message=message.encode(FORMAT)
       final_message_length=len(final_message)
       final_message_length=str(final_message_length).encode(FORMAT)
       final_message_length+=b' '*(HEADER-len(final_message_length))   
       conn.send(final_message_length)
       conn.send(final_message) 
      
      else:
       message=f"[SERVER] Username accepted. Welcome! {username}"
       final_message=message.encode(FORMAT)
       final_message_length=len(final_message)
       final_message_length=str(final_message_length).encode(FORMAT)
       final_message_length+=b' '*(HEADER-len(final_message_length))   
       conn.send(final_message_length)
       conn.send(final_message) 
       clients[username]=conn
       break

    print(f"[NEW-CONNECTION] {username} connected")
    if username!="admin":
     broadcast(f"🟢 {username} joined the chat.",username)
    welcome_msg=WELCOME_MESSAGE.encode('utf8')
    welcome_length=len(welcome_msg)
    welcome_length=str(welcome_length).encode(FORMAT)
    welcome_length+=b' '*(HEADER-len(welcome_length))
    conn.send(welcome_length)
    conn.send(welcome_msg)
    while True:
      rawdata=conn.recv(HEADER)       
       
      if not rawdata:
         connected=False
         if username in clients:
             del clients[username]
         if conn in admins:
            admins.remove(conn)  
         print(f"[Client {username}] disconnected")
         broadcast(f" 🔴 {username} left the chat. ",username)
         break
      msg_length=rawdata.decode(FORMAT)
      msg_length=int(msg_length)
      msg=conn.recv(msg_length).decode(FORMAT)

      if msg==DISCONNECT_MESSAGE:
        connected=False
        if conn in admins:
          admins.remove(conn)
        del clients[username] 
        print(f"[CLIENT {username}] disconnected ")
        broadcast(f" 🔴 {username} left the chat. ",username)
        break 
      print(f"{addr}[{username}]{msg}")
      if "/msg " in msg:
       msgPrivately(msg,username)
      elif "/users" in msg:
       listallusers(conn) 
      elif "/ban" in msg and conn in admins:
        handleBan(msg)
      elif "/kick" in msg and conn in admins:
        handleKick(msg)
      else:
       msg=f"[{username}] {msg}"
       broadcast(msg,username)
     
     
  conn.close()

def start():
  sock.listen()
  print(f"[LISTENING] Server is listening {SERVER}")
  while True:
    conn,addr=sock.accept()
    thread=threading.Thread(target=handleClient,args=(conn,addr),daemon=True)
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


print("[STARTING] Server is starting.....")
start()