import socket               # Import socket module
import os
import structures


packet_size = 500


def send_stop_wait(server_socket,client_addr,filename):
   file = open(filename,'r')
   file_content = file.read()
   packet_number =  0 ;
   buffer= ""
   while(packet_number<len(file_content)%packet_size):
      buffer = file_content[packet_number*packet_size:]



   while()
      structures.packet(seqno=0  )



s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)         # Create a socket object
host = socket.gethostname() # Get local machine name

file = open('server.in','r')

port = int(file.readline())
window_size = int(file.readline()) #in datagrams
random_seed = int(file.readline())
probability = float(file.readline())
connections_number = int(file.readline())


s.bind((host, port))        # Bind to the port




s.recvfrom(connections_number) # Now wait for client connection.



while True:


   data, addr = s.recvfrom(500)     # Establish connection with client.
   pid = os.fork()

   if(pid == 0):




