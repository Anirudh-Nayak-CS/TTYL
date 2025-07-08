import socket
import threading

HEADER=1024
PORT=5050
FORMAT="utf-8"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)
DISCONNECT_MESSAGE="/quit"
stop_thread=False
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(ADDR)
def receivemessages():
 global stop_thread
 while True:
   if stop_thread==True:
    break
   rawdata=sock.recv(HEADER)       
       
   if not rawdata:
    break
 
   msg_length=rawdata.decode(FORMAT)
   msg_length=int(msg_length)
   msg=sock.recv(msg_length).decode(FORMAT)
   print(f"\n{msg}")
    


def send(msg):
 if stop_thread==False:
  message=msg.encode(FORMAT)
  msg_length=len(message)
  send_length=str(msg_length).encode(FORMAT)  
  send_length+=b' '*(HEADER-len(send_length))
  sock.send(send_length)
  sock.send(message)
  

while True:

  username=input("Enter your username -> ") 
  username = username.strip() 
  username=username.replace(' ','_')
  user=username.encode(FORMAT)
  user_length=len(user)
  send_user_length=str(user_length).encode(FORMAT)
  send_user_length+=b' '*(HEADER-len(send_user_length))
  sock.send(send_user_length)
  sock.send(user)
 
  if username=="admin":
   password=input("Enter the admin's passsword: ")
   final_message=password.encode(FORMAT)
   final_message_length=len(final_message)
   final_message_length=str(final_message_length).encode(FORMAT)
   final_message_length+=b' '*(HEADER-len(final_message_length))   
   sock.send(final_message_length)
   sock.send(final_message)  
 
   server_pw_valid_msg_length=sock.recv(HEADER).decode(FORMAT)   
   server_pw_valid_msg_length=int(server_pw_valid_msg_length)
   server_pw_valid_msg=sock.recv(server_pw_valid_msg_length).decode(FORMAT)
   
   if server_pw_valid_msg=="Wrong password":
     print("Connection refused. Wrong password")
     stop_thread=True
     sock.close()
     exit()
   else:
    print(server_pw_valid_msg)
 
  msg_length=sock.recv(HEADER).decode(FORMAT)
  msg_length=int(msg_length)
  username_existence_msg=sock.recv(msg_length).decode(FORMAT)
  
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
   stop_thread=True
   sock.close()
   break
 elif "/kick" in message:
   if username=="admin":
    send(message)
   else:
    print("Commands can only be executed by an admin.")
 elif "/ban" in message:
  if username=="admin":
    send(message)
  else:
    print("Commands can only be executed by an admin.")
 else:
  send(message)
 
