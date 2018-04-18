import socket
import struct
import threading

def resend(my_socket,packet):
    my_socket.send(packet)



class packet:

    def __init__(self,length,seqno,data):
        self.length = struct.pack('H',length)
        self.seqno=struct.pack('I',seqno)
        self.data=data

        #data yet


input_file = open("client_input.txt",'r') #read the data of the client
server_ip = input_file.readline().split('\n')[0]
server_port = int(input_file.readline())
client_port = int(input_file.readline())
requested_filename = input_file.readline().split('\n')[0]
window_size = int(input_file.readline())#how many datagrams
input_file.close()






my_socket =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
my_socket.connect((server_ip,server_port))

my_packet = packet(len(requested_filename),0,requested_filename)

my_socket.send(my_packet)

timer = threading.Timer(10,resend,args=[my_socket,my_packet])

timer.start()

while()




#for i in range(30):
#   s.append( socket.socket(socket.AF_INET,socket.SOCK_STREAM))      # Create a socket object)
#    host = socket.gethostname() # Get local machine name
#port = 12348            # Reserve a port for your service.
#s[i].connect((host,port))
# rec=s[i].recv(1024)
#  print(rec)
#
