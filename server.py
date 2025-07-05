import socket
import threading

HEADER=1024
PORT=5050
FORMAT="utf-8"
DISCONNECT_MESSAGE="!DISCONNECTED"

SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(ADDR)


def handleClient(conn,addr):
  print(f"[NEW-CONNECTION] {addr} connected")
  connected=True
  while connected:
    msg_length=conn.recv(HEADER).decode(FORMAT)
    if msg_length:
     msg_length=int(msg_length)
     msg=conn.recv(msg_length).decode(FORMAT)
     if msg==DISCONNECT_MESSAGE:
      connected=False
     print(f"[{addr}]{msg}")
     conn.send("Msg received ".encode(FORMAT))
  conn.close()

def start():
  sock.listen(1)
  print(f"[LISTENING] Server is listening {SERVER}")
  while True:
    conn,addr=sock.accept()
    thread=threading.Thread(target=handleClient,args=(conn,addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")


print("[STARTING] Server is starting.....")
start()