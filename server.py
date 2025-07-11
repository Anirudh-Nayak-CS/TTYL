#importing modules
import socket
import threading


#defining constants
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

#storing client,admin,banned connections
clients={}
admins=[]
banned_usernames=[]

#binding the socket
SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(ADDR)

#function to send a message to the client
def sendMessage(conn,message):
    final_message=message.encode(FORMAT)
    final_message_length=len(final_message)
    final_message_length=str(final_message_length).encode(FORMAT)
    final_message_length+=b' '*(HEADER-len(final_message_length))   
    conn.send(final_message_length)
    conn.send(final_message) 


#function to broadcast the message
def broadcast(message,currclientusername):
  for username,conn in clients.items():
    if username!=currclientusername:
      sendMessage(conn,message)


#listing all users
def listallusers(conn):
  online_users=', '.join(clients.keys())
  message=f"{online_users}"
  sendMessage(conn,message)


#function for private conversation
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
   message=f"[Private message from {currclientusername}] {actualmessage}"
   sendMessage(connection_receiver,message)
   
   confirmation_message=f"Your message was sent to {user} successfully"
   sendMessage(connection_sender,confirmation_message)


#handling /kick
def handleKick(msg,connection):
  msg_parts=msg.split(' ')
  if len(msg_parts)<2:
    return
  username=msg_parts[1]
  if username!="admin" and username in clients:
    kick_user_conn=clients[username]
    del clients[username]
    message="You were kicked by an admin."
    sendMessage(kick_user_conn,message)
    sendMessage(kick_user_conn,DISCONNECT_MESSAGE) 
    kick_broadcast_msg=f"👢 {username} was kicked from the server."
    broadcast(kick_broadcast_msg,username)  
    kick_user_conn.close()
    return
  else :
    sendMessage(connection,"User not online")  


#handling /ban
def handleBan(msg,connection):
  msg_parts=msg.split(' ')
  if len(msg_parts)<2:
    return
  username=msg_parts[1]
  if username!="admin" and username in clients:
    ban_user_conn=clients[username]
    banned_usernames.append(username)
    del clients[username]
    message="You were banned by an admin."
    sendMessage(ban_user_conn,message)
    sendMessage(ban_user_conn,DISCONNECT_MESSAGE) 
    ban_broadcast_msg=f"🔨 {username} was banned from the server."
    broadcast(ban_broadcast_msg,username)  
    ban_user_conn.close()
    return
  else :
    sendMessage(connection,"User not online")  


#main logic
def handleClient(conn,addr):

  connected=True
  while connected:

    #checks on username
    while True:
     username_length=conn.recv(HEADER).decode(FORMAT)

     if username_length:
      username_length=int(username_length)
      username=conn.recv(username_length).decode(FORMAT)
       
      if username in banned_usernames:
        message="You are banned from the server."
        sendMessage(conn,message)
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
          sendMessage(conn,message)
          clients["admin"] = conn 
          admins.append(conn)
          break

        else :
         message="Wrong password"
         sendMessage(conn,message)
         conn.close()
         return 

      elif username in clients:
       message="[SERVER] Username already exists. Please enter another username."
       sendMessage(conn,message)
      
      else:
       message=f"[SERVER] Username accepted. Welcome! {username}"
       sendMessage(conn,message)
       clients[username]=conn
       break
   

   #Informing  other users when someone joins or leaves the chat
    print(f"[NEW-CONNECTION] {username} connected")
    if username!="admin":
     broadcast(f"🟢 {username} joined the chat.",username)
    
    sendMessage(conn,WELCOME_MESSAGE)
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
      

      #handling the message appropriately 
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
        handleBan(msg,conn)
      elif "/kick" in msg and conn in admins:
        handleKick(msg,conn)
      else:
       msg=f"[{username}] {msg}"
       broadcast(msg,username)
          
  conn.close()


#start of connection b/w client and server
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