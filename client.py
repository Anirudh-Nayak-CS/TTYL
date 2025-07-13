#importing modules
import socket
import threading
import rsa

#defining constants
HEADER=1024
PORT=5050
FORMAT="utf-8"
SERVER="127.0.1.1"
ADDR=(SERVER,PORT)
DISCONNECT_MESSAGE="/quit"
stop_thread=False
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
public_key,private_key=rsa.newkeys(1024)
public_partner=None
sock.connect(ADDR)


#function to send a message to the server
def sendmessages(message,sock):
   final_message=message.encode(FORMAT)
   final_message_length=len(final_message)
   final_message_length=str(final_message_length).encode(FORMAT)
   final_message_length+=b' '*(HEADER-len(final_message_length))   
   sock.send(final_message_length)
   sock.send(final_message)  


#function to receive the message from server
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
   if msg==DISCONNECT_MESSAGE:
    stop_thread=True
    sock.close()
    exit()
   else:
    print(f"\n{msg}")
   

def send(msg):
 if stop_thread==False:
  sendmessages(msg,sock)
  

#main logic
while True:

  #taking username and validating admin password
  username=input("Enter your username -> ") 
  username = username.strip() 
  username=username.replace(' ','_')
  sendmessages(username,sock)
 
  if username=="admin":
   password=input("Enter the admin's passsword: ")
   sendmessages(password,sock)  
 
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


#taking further inputs  
welcomemsg_length=sock.recv(HEADER).decode(FORMAT)
if welcomemsg_length:
  welcomemsg_length=int(welcomemsg_length)
  welcomemsg=sock.recv(welcomemsg_length).decode(FORMAT)

else :
  sock.close()
  exit()

print(welcomemsg)
thread=threading.Thread(target=receivemessages)
thread.start()
while True:
 try:
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
 except(EOFError,ValueError):
  break

 
