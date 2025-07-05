import socket

HEADER=1024
PORT=5050
FORMAT="utf-8"
DISCONNECT_MESSAGE="!DISCONNECTED"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(ADDR)


def send(msg):
  message=msg.encode(FORMAT)
  msg_length=len(message)
  send_length=str(msg_length).encode(FORMAT)   #sending the length of msg
  send_length+=b' '*(HEADER-len(send_length))
  sock.send(send_length)
  sock.send(message)
  print(sock.recv(2048).decode(FORMAT))

send("Hello world!")
send("lol")
send("tall")
send(DISCONNECT_MESSAGE)