import socket

HEADER=1024
PORT=5050
FORMAT="utf-8"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)
DISCONNECT_MESSAGE="/quit"

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(ADDR)


def send(msg):
  message=msg.encode(FORMAT)
  msg_length=len(message)
  send_length=str(msg_length).encode(FORMAT)  
  send_length+=b' '*(HEADER-len(send_length))
  sock.send(send_length)
  sock.send(message)
  print(sock.recv(2048).decode(FORMAT))

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
while True:
 message=input("\nEnter your message -> ")
 if message=="/quit":
   send(DISCONNECT_MESSAGE)
   break
 send(message)
 
