import socket               # Import socket module
import os
import struct

def unpack_helper(fmt, data):
    size = struct.calcsize(fmt)
    print()
    print(size)
    return struct.unpack(fmt, data[:size]), data[size:]

class Packet:

    def __init__(self,length=0,seqno=0,data=''):
        self.length = struct.pack('H',length)
        self.seqno=struct.pack('I',seqno)
        self.data=data


s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)         # Create a socket object
host = socket.gethostbyname('localhost') # Get local machine name

file = open('server.in','r')

port = int(file.readline())
window_size = int(file.readline()) #in datagrams
random_seed = int(file.readline())
probability = float(file.readline())

file.close()
            # Reserve a port for your service.
s.bind((host, port))  # Bind to the port
print('Waiting for connection')
m, adr = s.recvfrom(port)
p = Packet()
h,d = unpack_helper('HI',m)
print(h)
print(d.decode())

# print(s.recvfrom())
# s.send('hello')