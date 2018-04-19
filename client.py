import socket
import struct
import threading
from structures import packet
import structures

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
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_socket.connect((self.server_ip,self.server_port))
        input_file.close()


    def send_request(self):
        request_packet = packet(seqno=0, data=self.requested_filename)
        request_pack = request_packet.pack()
        self.my_socket.send(request_pack)


client = Client('client.in')
client.send_request()


while True:

    received_pack , addr=client.my_socket.recvfrom(600)
    received_packet = packet(pkd_data=received_pack)
    if(received_packet.checksum==structures.calc_checksum(received_packet.data)):
        print(received_packet.data)
        ack_packet = structures.ack(checksum=received_packet.checksum)
        client.my_socket.send(ack_packet.pack())


client.my_socket.close()
#timeout = threading.Timer(10,client.send_request)

#timeout.start()

