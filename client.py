import socket
import struct
import threading

def resend(my_socket,packet):
    my_socket.send(packet)


class Packet:

    def __init__(self,length,seqno,data):
        self.length = length
        self.seqno=seqno
        self.data=data

        #data yet

class Client:

    def __init__(self,file_name):
        input_file = open(file_name,'r') #read the data of the client
        self.server_ip = input_file.readline().split('\n')[0]
        self.server_port = int(input_file.readline())
        self.client_port = int(input_file.readline())
        self.requested_filename = input_file.readline().split('\n')[0]
        self.window_size = int(input_file.readline())#how many datagrams
        input_file.close()






cl = Client("client.in")
my_socket =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
my_socket.connect((cl.server_ip,cl.server_port))
my_packet = Packet(len(cl.requested_filename),0,('hamadadadadaadada'))
lent = len(my_packet.data.encode())
formats = "HI%ds" %lent
packet_bytes = struct.pack(formats,my_packet.length,my_packet.seqno,my_packet.data.encode())
print(packet_bytes)

my_socket.send(packet_bytes)

print(my_socket.recv(cl.server_port))
# timer = threading.Timer(10,resend,args=[my_socket,my_packet])

# timer.start()

# while()




#for i in range(30):
#   s.append( socket.socket(socket.AF_INET,socket.SOCK_STREAM))      # Create a socket object)
#    host = socket.gethostname() # Get local machine name
#port = 12348            # Reserve a port for your service.
#s[i].connect((host,port))
# rec=s[i].recv(1024)
#  print(rec)
#
