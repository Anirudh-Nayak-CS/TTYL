#importing modules
import socket
import threading
import math
import datetime
import emoji

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env

# Load private key from .env
private_key_path = os.getenv("PRIVATE_KEY_PATH")
if not private_key_path or not os.path.exists(private_key_path):
    raise ValueError("Missing or invalid PRIVATE_KEY_PATH in .env")

with open(private_key_path, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())



#defining constants
HEADER=1024
PORT=5050
FORMAT="utf-8"
DISCONNECT_MESSAGE="/quit"
WELCOME_MESSAGE = (
  "\n╔══════════════════════════════════════════════════════════════════╗\n"
    "║                        Welcome to TTYL                           ║\n"
    "╠══════════════════════════════════════════════════════════════════╣\n"
    "║ Commands:                                                        ║\n"
    "║ /quit                      → Disconnect from server              ║\n"
    "║ /msg <username> msg        → Privately message a user            ║\n"
    "║ /users                     → List of users online                ║\n"
    "║ /vote <username>           → Cast vote to kick <username>        ║\n"
    "║ /changename <new username> → Change your username                ║\n"
    "║ /kick <username>           → Kick a user (admin & moderator only)║\n"
    "║ /ban <username>            → Ban a user (admin only)             ║\n"
    "║ /warn <username> <msg>     → Warn a user (moderator only)        ║\n"
    "║ /mute <username> <minutes> → Mute a user (moderator only)        ║\n"  
    "╚══════════════════════════════════════════════════════════════════╝"
)
emoji_list={  
    ":smile:": "😄",
    ":laugh:": "😂",
    ":sad:": "😢",
    ":angry:": "😠",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":clap:": "👏",
    ":fire:": "🔥",
    ":star:": "⭐",
    ":ok:": "👌",
    ":wave:": "👋",
    ":eyes:": "👀",
    ":sleep:": "😴",
    ":sunglasses:": "😎"
    }

#storing client,admin,banned connections
clients={}
admins=[]
moderators=[]
muted_users=set()
banned_usernames=[]
votecount={}

#binding the socket
SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ADDR)

#crypto
def encrypt_for_log(msg: str) -> str:
    encrypted = public_key.encrypt(
        msg.encode(FORMAT),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted.hex()


#function to convert a sentence to emoji (if present)
def convert2emoji(msg):
  return emoji.emojize(msg,language='alias')

#function to send a message to the client
def sendMessage(conn,message):
    if message=="/quit":
      final_message=message.encode(FORMAT)
      final_message_length=len(final_message)
      final_message_length=str(final_message_length).encode(FORMAT)
      final_message_length+=b' '*(HEADER-len(final_message_length))   
      conn.send(final_message_length)
      conn.send(final_message)  
      return
    message=convert2emoji(message)
    timestamp=datetime.datetime.now().strftime("[%H:%M:%S]")
    message=f"{timestamp} {message}"
    final_message=message.encode(FORMAT)
    final_message_length=len(final_message)
    final_message_length=str(final_message_length).encode(FORMAT)
    final_message_length+=b' '*(HEADER-len(final_message_length))   
    conn.send(final_message_length)
    conn.send(final_message) 

#function to warn user
def handleWarn(msg,conn):
  parts=msg.split(' ',2)
  if len(parts)!=3:
    sendMessage(conn,"[SERVER] Invalid format. Use /warn <username> <message>.")
    return
  message=parts[2]
  user=parts[1]
  if user not in clients:
    sendMessage(conn,f"{user} is not online.")
    return
  warning_user_conn=clients[user]
  sendMessage(warning_user_conn,'WARNING❗❗'+message)
  sendMessage(conn,f"Successfully warned {user}.")

#function to mute a user
def handleMute(msg,conn):
  parts=msg.split(' ',2)
  if len(parts)!=3:
    sendMessage(conn,"[SERVER] Invalid format. Use /mute <username> <duration(minutes)>.")
    return
  try:
   time=int(parts[2])
  except ValueError:
   sendMessage(conn,"The duration(mins) should be an integer.")
   return
  user=parts[1]
  if user not in clients:
    sendMessage(conn,f"{user} is not online.")
    return
  mute_user_conn=clients[user]
  broadcast(f"🔇🔇🔇 {user} has been muted for {time} minutes by the moderator.",user)  
  muted_users.add(user)
  sendMessage(mute_user_conn,f"🔇🔇🔇 You have been muted for {time} minutes by the moderator.")


  timer=threading.Timer(time*60,unmute_user,args=(user,))
  timer.start()
  sendMessage(conn,f"Succuessfully muted {user} for {time} minutes.")

#function to unmute a user
def unmute_user(username):
  if username in muted_users:
   muted_users.discard(username)
   if username in clients:
     sendMessage(clients[username],f"🔊🔊🔊 You have been unmuted.")

#function to change username
def changeUsername(msg,conn,username):
   parts=msg.split(' ',1)
   message_length=len(parts)
   if message_length!=2:
     sendMessage(conn,"[SERVER] Invalid format. Use /changename <new username>.")
     return username
   new_name=parts[1]

   if new_name in  clients:
     sendMessage(conn,"[SERVER] Username exists. Try another username.")
     return username
   elif new_name=="admin" or new_name=="moderator":
     sendMessage(conn,"[SERVER] You can't change your name to be an admin/moderator.")
     return username
   clients.pop(username)
   clients[new_name]=conn
   sendMessage(conn,f"[SERVER] Your username has been changed to {new_name}")
   broadcast(f"{username} changed their name to {new_name}",new_name)
   return new_name


#function to check the number of votes recieved by a  user to kick him/her
def checkVoteforKick(message,conn,username):

   parts=message.split(' ',1)
   message_length=len(parts)
   if message_length!=2:
     sendMessage(conn,"[SERVER] Invalid format. Use /vote <username>.")
     return
   vote_username=parts[1]
   if vote_username=="admin" or vote_username=="moderator":
       sendMessage(conn,"You can't kick an admin or a moderator.")
       return
   if vote_username not in votecount.keys():
     votecount[vote_username]=1
     broadcast(f"[SERVER] {vote_username} Received {votecount[vote_username]}/{math.ceil(len(clients)/2)} votes for getting kicked.",username)   
     sendMessage(conn,f"[SERVER] {vote_username} Received {votecount[vote_username]}/{math.ceil(len(clients)/2)} votes for getting kicked.")  
   else:
    votecount[vote_username]+=1
    broadcast(f"[SERVER] {vote_username} Received {votecount[vote_username]}/{math.ceil(len(clients)/2)} votes for getting kicked.",username)   
    sendMessage(conn,f"[SERVER] {vote_username} Received {votecount[vote_username]}/{math.ceil(len(clients)/2)} votes for getting kicked.")
   if votecount[vote_username] >= len(clients)/2:
     handleKickByVote("You were kicked from chat due to majority vote by other users. ",vote_username)

#handle kick by vote
def handleKickByVote(message,username):
     if username not in clients:
       return
   
     kick_user_conn=clients[username]
     del clients[username]
     sendMessage(kick_user_conn,message)
     sendMessage(kick_user_conn,DISCONNECT_MESSAGE)
     kick_user_conn.close() 
     kick_broadcast_msg=f"👢 {username} was kicked from the server."
     broadcast(kick_broadcast_msg,username)  
     votecount[username]=0 
     

#function to broadcast the message 
def broadcast(message, currclientusername):
    if currclientusername in muted_users and currclientusername != "admin":
      return

    for username, conn in clients.items():
        if username not in muted_users and username!=currclientusername:
            sendMessage(conn, message)



#listing all users
def listallusers(conn):
  online_users=', '.join(clients.keys())
  message=f"{online_users}"
  sendMessage(conn,message)


#function for private conversation
def msgPrivately(message,currclientusername):
  msg_parts=message.split(' ',2)
  
  connection_sender=clients[currclientusername]
  if len(msg_parts)!=3:
    sendMessage(connection_sender,"[SERVER] Invalid format.Use /msg <username> msg")
    return
  
  user=msg_parts[1]
  actualmessage=msg_parts[2]
  if user not in clients:
   sendMessage(connection_sender,"[SERVER] User is not online")
  else:  
   connection_receiver=clients[user]
   message=f"[Private message from {currclientusername}] {actualmessage}"
   sendMessage(connection_receiver,message)
   
   confirmation_message=f"Your message was sent to {user} successfully"
   sendMessage(connection_sender,confirmation_message)




#handling /kick
def handleKickByAdminandMod(msg,connection):
    if msg.startswith('/kick '):
        msg_parts = msg.split(' ')
        if len(msg_parts) != 2:
            sendMessage(connection, "[SERVER] Invalid format. Use /kick <username>")
            return

        username = msg_parts[1]
        if username != "admin" and username in clients:
            kick_user_conn = clients[username]

            # Notify user first
            sendMessage(kick_user_conn, "You were kicked by an admin/mod.")
            sendMessage(kick_user_conn, DISCONNECT_MESSAGE)
            del clients[username]
            kick_user_conn.close()
           
            # Broadcast to everyone
            kick_broadcast_msg = f"👢 {username} was kicked from the server."
            broadcast(kick_broadcast_msg, username)
            
        else:
            sendMessage(connection, "[SERVER] User not online or cannot kick admin.")



#handling /ban
def handleBan(msg, connection):
    msg_parts = msg.split(' ')
    if len(msg_parts) != 2:
        sendMessage(connection, "[SERVER] Invalid format. Use /ban <username>")
        return

    username = msg_parts[1]
    if username != "admin" and username in clients:
        ban_user_conn = clients[username]

        # Add to banned list early
        banned_usernames.append(username)

        # Notify the user first
        sendMessage(ban_user_conn, "You were banned by an admin.")
        sendMessage(ban_user_conn, DISCONNECT_MESSAGE)
        del clients[username]
        ban_user_conn.close()
        # Broadcast to others
        ban_broadcast_msg = f"🔨 {username} was banned from the server."
        broadcast(ban_broadcast_msg, username)
        
    else:
        sendMessage(connection, "[SERVER] User not online or cannot ban admin.")



#main logic
def handleClient(conn,addr):

  connected=True
  while connected:

    #checks on username
    while True:
     username_length=conn.recv(HEADER).decode(FORMAT).strip()
     if not username_length:
        conn.close()
        return
    
     username_length=int(username_length)
     username=conn.recv(username_length).decode(FORMAT)
     
     if username in banned_usernames:
       message="You are banned from the server."
       sendMessage(conn,message)
       conn.close()
       return
      
    #checks if username is an admin
     elif username=="admin": 
       rawdata=conn.recv(HEADER).strip()       
      
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
     
    #checks if username is an moderator
     elif username=="moderator": 
       rawdata=conn.recv(HEADER).strip()       
      
       if not rawdata:
        connected=False
        if username in clients:
            del clients[username]
        if conn in moderators:
           moderators.remove(conn)  
        print(f"[Client {username}] disconnected")
        broadcast(f" 🔴 {username} left the chat. ",username)
        break
       password_length=int(rawdata.decode(FORMAT))
       password=conn.recv(password_length).decode(FORMAT)
        
       if password=="modpassword":
         message="Welcome Moderator!"
         sendMessage(conn,message)
         clients[username] = conn 
         moderators.append(conn)
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
    if username not in ["admin","moderator"]:
     broadcast(f"🟢 {username} joined the chat.",username)
    
    sendMessage(conn,WELCOME_MESSAGE)
    while True:
      rawdata=conn.recv(HEADER).strip()       
       
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
      msg_length=rawdata.decode(FORMAT).strip()
      msg_length=int(msg_length)
      msg=conn.recv(msg_length).decode(FORMAT)

      if msg==DISCONNECT_MESSAGE:
        connected=False
        if conn in admins:
          admins.remove(conn)
        elif conn in moderators:
          moderators.remove(conn)
        del clients[username] 
        print(f"[CLIENT {username}] disconnected ")
        broadcast(f" 🔴 {username} left the chat. ",username)
        break 
      log_msg = f"{addr}[{username}] {msg}"
      encrypted_log = encrypt_for_log(log_msg)
      print(f"[ENCRYPTED LOG] {encrypted_log}")
      print()
      if msg.startswith("/msg "):
       msgPrivately(msg,username)
      elif msg=="/users":
       listallusers(conn) 
      elif msg.startswith("/vote "):
        checkVoteforKick(msg,conn,username)
      elif msg.startswith("/changename "):
        username=changeUsername(msg,conn,username)
      elif msg.startswith("/ban ") and conn in admins:
        print("trying to ban")
        handleBan(msg,conn)
      elif msg.startswith("/kick ") and (conn in admins or conn in moderators):
        print("trying to kick")
        handleKickByAdminandMod(msg,conn)
      elif msg.startswith("/mute ")  and conn in moderators:
        handleMute(msg,conn)
      elif msg.startswith("/warn ") and conn in moderators:
        handleWarn(msg,conn)
      else:
       msg=f"[{username}] {msg}"
       broadcast(msg,username)
  votecount[username]=0        
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