from socket import socket
import struct
import threading
from structures import packet

def resend(my_socket,packet):
    my_socket.send(packet)


class Client:

    def __init__(self,file_name):
        input_file = open(file_name,'r') #read the data of the client
        self.server_ip = input_file.readline().split('\n')[0]
        self.server_port = int(input_file.readline())
        self.client_port = int(input_file.readline())
        self.requested_filename = input_file.readline().split('\n')[0]
        self.window_size = int(input_file.readline())#how many datagrams
        input_file.close()


    def fork_n_clients(self,file_name,n=10):
        for i in range(0,n):
            cl = Client(file_name)
            cl_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
            cl_socket.connect((cl.server_ip,cl.server_port))
            cl_packet = packet(seqno=0,data=cl.requested_filename)
            pkd_packet = cl_packet.pack()
            cl_socket.send(pkd_packet)
            cl_socket.close()


Client.fork_n_clients('client.in',20)