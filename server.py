import socket
import threading

HEADER=1024
PORT=5050
FORMAT="utf-8"
DISCONNECT_MESSAGE="/quit"
WELCOME_MESSAGE=(
  "*******************************************"
   "\n"
   "Commands \n"
   "/quit -> to disconnect from server \n"
  "*******************************************"
)



clients={}

SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(ADDR)

def broadcast(message,currclientusername):
  final_message=f"[{currclientusername}] {message}".encode(FORMAT)
  final_message_length=len(final_message)
  final_message_length=str(final_message_length).encode(FORMAT)
  final_message_length+=b' '*(HEADER-len(final_message_length))
  for username,conn in clients.items():
    if username!=currclientusername:
       
       conn.send(final_message_length)
       conn.send(final_message)

def handleClient(conn,addr):
  print(f"[NEW-CONNECTION] {addr} connected")
  connected=True
  while connected:
    while True:
     username_length=conn.recv(HEADER).decode(FORMAT)

     if username_length:
      username_length=int(username_length)
      username=conn.recv(username_length).decode(FORMAT)

      if username in clients:
       conn.send("[SERVER] Username already exists. Please enter another username.".encode(FORMAT))
      
      else:
       conn.send(f"[SERVER] Username accepted. Welcome! {username}".encode(FORMAT))
       clients[username]=conn
       break

    welcome_msg=WELCOME_MESSAGE.encode('utf8')
    welcome_length=len(welcome_msg)
    welcome_length=str(welcome_length).encode('utf-8')
    welcome_length+=b' '*(HEADER-len(welcome_length))
    conn.send(welcome_length)
    conn.send(welcome_msg)
    while True:
     msg_length=conn.recv(HEADER).decode(FORMAT)
     if not msg_length:
       continue 
     msg_length=int(msg_length)
     msg=conn.recv(msg_length).decode(FORMAT)

     if msg==DISCONNECT_MESSAGE:
        connected=False
        del clients[username] 
        print(f"[CLIENT {username}] disconnected ")
        break 
     print(f"{addr}[{username}]{msg}")
     broadcast(msg,username)
     
     
  conn.close()

def start():
  sock.listen()
  print(f"[LISTENING] Server is listening {SERVER}")
  while True:
    conn,addr=sock.accept()
    thread=threading.Thread(target=handleClient,args=(conn,addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


print("[STARTING] Server is starting.....")
start()