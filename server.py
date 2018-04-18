import socket               # Import socket module
import os
import structures


packet_size = 500

def send_stop_wait(server_socket,client_addr,filename):
   file = open(filename,'r')
   file_content = file.read()
   packet_number =  0 ;
   buffer= ""
   seqno = 0
   while(packet_number<len(file_content)%packet_size):
      start_index = packet_number*packet_size
      end_index = packet_number * packet_size + packet_size - 1
      if(end_index<=len(file_content)):
         buffer = file_content[start_index:end_index]
      else:
         buffer = file_content[start_index:]
      my_packet = structures.packet(seqno=0,length=len(buffer),data=buffer)
      server_socket.sendto(my_packet,addr)

      server_socket.sendto()



   while():
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


   request_data, addr = s.recvfrom(500)     # Establish connection with client.
   pid = os.fork()

   request_packet = structures.packet(packed_data = request_packet)

   if(pid == 0):
      send_stop_wait(s,addr,data)





