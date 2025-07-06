import socket
import threading

HEADER=1024
PORT=5050
FORMAT="utf-8"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)
DISCONNECT_MESSAGE="/quit"

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(ADDR)
def receivemessages():
 while True:
   msg_length=sock.recv(HEADER).decode(FORMAT)
   if msg_length:
    msg_length=int(msg_length)
    msg=sock.recv(msg_length).decode(FORMAT)
    print(f"\n{msg}")
    
   else:
     break

def send(msg):
  message=msg.encode(FORMAT)
  msg_length=len(message)
  send_length=str(msg_length).encode(FORMAT)  
  send_length+=b' '*(HEADER-len(send_length))
  sock.send(send_length)
  sock.send(message)
  

while True:

 username=input("Enter your username -> ")
 user=username.encode(FORMAT)
 user_length=len(user)
 send_user_length=str(user_length).encode(FORMAT)
 send_user_length+=b' '*(HEADER-len(send_user_length))
 sock.send(send_user_length)
 sock.send(user)
 username_existence_msg=sock.recv(1024).decode(FORMAT)
 if "Username already exists" in username_existence_msg:
    print(username_existence_msg)
    continue
 else:
  print(username_existence_msg)
  break
 
welcomemsg_length=sock.recv(HEADER).decode(FORMAT)
welcomemsg_length=int(welcomemsg_length)
welcomemsg=sock.recv(welcomemsg_length).decode(FORMAT)
print(welcomemsg)
thread=threading.Thread(target=receivemessages)
thread.start()
while True:
 message=input()
 if message=="/quit":
   send(DISCONNECT_MESSAGE)
   break
 send(message)
 
