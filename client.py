import socket

HEADER=1024
PORT=5050
FORMAT="utf-8"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)


sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(ADDR)


def send(username,msg):
  user=username.encode(FORMAT)
  user_length=len(user)
  send_user_length=str(user_length).encode(FORMAT)
  send_user_length+=b' '*(HEADER-len(send_user_length))
  sock.send(send_user_length)
  sock.send(user)
  message=msg.encode(FORMAT)
  msg_length=len(message)
  send_length=str(msg_length).encode(FORMAT)  
  send_length+=b' '*(HEADER-len(send_length))
  sock.send(send_length)
  sock.send(message)
  print(sock.recv(2048).decode(FORMAT))

while True:
 
 username=input("Enter your username")
 print(f"Welcome {username}")
 welcomemsg_length=sock.recv(HEADER).decode(FORMAT)
 welcomemsg_length=int(welcomemsg_length)
 welcomemsg=sock.recv(welcomemsg_length).decode(FORMAT)
 print(welcomemsg)
 message=input("Enter your message")
 send(username,message)
 
