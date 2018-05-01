import socket
import struct
import threading
from structures import packet, ack, calc_checksum
import structures

def resend(my_socket,packet):
    my_socket.send(packet())


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
        self.recv_pkt_list = []

        input_file.close()


    def send_request(self):
        request_packet = packet(seqno=0, data=self.requested_filename)
        request_pack = request_packet.pack()
        self.my_socket.send(request_pack)
        print('File: ' + str(self.requested_filename) + ' has been requested from the server.')

    def recv_file_len(self, socket):
        pkt, adr = socket.recvfrom(600)
        unpkd = packet(pkd_data=pkt,type='bytes')
        ack_p = ack(checksum=calc_checksum(unpkd.data.decode()),seqno=0).pack()
        socket.send(ack_p)
        self.file_len = int(unpkd.data)
        print('Required file length = ', self.file_len, ' packets.')

    def recv_go_back_n(self):
        client.recv_file_len(self.my_socket)
        print('Connected to socket #' + str(self.my_socket.getsockname()[1]))
        self.my_socket.settimeout(5)
        exp_pkt_num = 0
        while True:
            try:
                pkt, adr = self.my_socket.recvfrom(600)
                recv_pkt = packet(pkd_data=pkt, type='bytes')
                if adr[0] == self.server_ip:
                    cs = recv_pkt.checksum
                    ack_pkt= ack(seqno=recv_pkt.seqno, checksum=cs)
                    pkd_ack = ack_pkt.pack()
                    if recv_pkt.seqno == exp_pkt_num and recv_pkt.checksum == calc_checksum(recv_pkt.data, type='bytes'):
                        self.recv_pkt_list.append(recv_pkt)
                        print('Received packet# ' + str(recv_pkt.seqno))
                        self.my_socket.send(pkd_ack)
                        exp_pkt_num += 1
                    else:
                        continue
                if self.file_len == len(self.recv_pkt_list):
                    print('File received successfully.')
                    break
            except socket.timeout:
                print('Packet# ', exp_pkt_num, ' timed out, re-receiving.')
                continue

    def write_file(self, pkt_list):
        file = open('dl_' + str(self.requested_filename), 'wb')
        for pkt in pkt_list:
            file.write(pkt.data)
        print('File Written!')


client = Client('client.in')
client.send_request()
received_pack , addr = client.my_socket.recvfrom(600)
received_packet = packet(pkd_data=received_pack)

server_new_port = int(received_packet.data)
print('New port number: ',server_new_port)

client.my_socket.connect((client.server_ip,server_new_port))

seqno = 0
while True:

    received_pack , addr = client.my_socket.recvfrom(600)
    received_packet = packet(pkd_data=received_pack)
    if(received_packet.checksum==structures.calc_checksum(received_packet.data) and received_packet.seqno==seqno):
        print(received_packet.data)
        ack_packet = structures.ack(seqno= seqno,checksum=received_packet.checksum)
        client.my_socket.send(ack_packet.pack())
        seqno=(seqno+1)%2
    elif(received_packet.seqno!= seqno):
        client.my_socket.send(ack_packet.pack())

# client.recv_go_back_n()
# client.write_file(client.recv_pkt_list)


client.my_socket.close()
