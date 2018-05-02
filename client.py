import socket
import struct
import threading
from structures import packet, ack, calc_checksum
import structures
import random
def resend(my_socket,packet):
    my_socket.send(packet())

def arrange_window(window,base):

    temp1 = []
    temp2 = []
    window.sort()
    for i in window:
        if(i.seqno>=base):
            temp1.append(i)
        else:
            temp2.append(i)
    window=temp1+temp2
    return


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

    def get_corrupted_packets(self,packets_num, probability, seed):
        random.seed(seed)
        corrupted = random.sample(range(packets_num), int(probability * packets_num))
        corrupted = [i for i in corrupted]
        corrupted.sort()
        return corrupted

    def recv_file_len(self, socket):
        pkt, adr = socket.recvfrom(600)
        unpkd = packet(pkd_data=pkt,type='bytes')
        ack_p = ack(checksum=calc_checksum(unpkd.data.decode()),seqno=0).pack()
        socket.send(ack_p)
        self.file_len = int(unpkd.data)
        print('Required file length = ', self.file_len, ' packets.')
    ##################
    def recv_selective_repeat(self,params):

        window_size = params[0]

        packet_number = 0;
        buffer = ""  # divides file content into chunks of packet size
        next_seqno = 0
        send = True
        file_content = ""
        window = []
        window_seqno = []

        recv_base = 0

        while True:

            while (len(window) < window_size):  # fills window

                received_pack, addr = self.my_socket.recvfrom(600)

                received_packet = packet(pkd_data=received_pack)

                if (received_packet.checksum == structures.calc_checksum(
                        received_packet.data)):
                    ack_packet = structures.ack(seqno=received_packet.seqno, checksum=received_packet.checksum)
                    client.my_socket.send(ack_packet.pack())
                    if(not (received_packet.seqno in window_seqno)):
                        print(received_packet.data)
                        window.append(received_packet)
                        window_seqno.append(received_packet.seqno)

                    # seqno = (seqno + 1) % 2
                #elif (received_packet.seqno in window_seqno):
                 #   client.my_socket.send(ack_packet.pack())




                #seqno = (seqno + 1) % window_size
                #packet_number = packet_number + 1

            arrange_window(window,recv_base)

            while(recv_base==window[0].seqno):
                window.pop(0)
                window_seqno.remove(recv_base)
                recv_base=(recv_base+1)/window_size





##########################################################
    def recv_go_back_n(self):
        client.recv_file_len(self.my_socket)
        print('Connected to socket #' + str(self.my_socket.getsockname()[1]))
        corrupted = self.get_corrupted_packets(self.file_len,0.2,5)
        exp_pkt_num = 0
        while True:
            try:
                pkt, adr = self.my_socket.recvfrom(600)
                recv_pkt = packet(pkd_data=pkt, type='bytes')
                if recv_pkt.seqno in corrupted:
                    recv_pkt.checksum = recv_pkt.checksum-10
                    corrupted.remove(recv_pkt.seqno)
                if adr[0] == self.server_ip:
                    print('Received packet# '+str(recv_pkt.seqno)) # receive packets initally.
                    cs = recv_pkt.checksum
                    ack_pkt= ack(seqno=recv_pkt.seqno, checksum=cs)
                    pkd_ack = ack_pkt.pack()
                    if recv_pkt.seqno == exp_pkt_num and recv_pkt.checksum == calc_checksum(recv_pkt.data, type='bytes'):
                        print('Sending Ack# ' + str(recv_pkt.seqno))
                        self.recv_pkt_list.append(recv_pkt) # if packets not corrupted and came in order, add to list.
                        self.my_socket.send(pkd_ack) # and send ack
                        exp_pkt_num += 1
                    else:  # else discard packet, will be received again.
                        if recv_pkt.checksum != calc_checksum(recv_pkt.data,type='bytes'):
                            print('Packet # ', recv_pkt.seqno,'is corrupted, re-receiving')
                        continue
                if self.file_len == len(self.recv_pkt_list): # if all file received, break.
                    print('File received successfully.')
                    break
            except socket.timeout:
                print('Packet# ', exp_pkt_num, ' timed out, re-receiving.')
                continue

    #################################

    def stop_wait(self):
        seqno = 0
        while True:

            received_pack, addr = client.my_socket.recvfrom(600)
            received_packet = packet(pkd_data=received_pack)
            if (received_packet.checksum == structures.calc_checksum(
                    received_packet.data) and received_packet.seqno == seqno):
                print(received_packet.data)
                ack_packet = structures.ack(seqno=seqno, checksum=received_packet.checksum)
                client.my_socket.send(ack_packet.pack())
                seqno = (seqno + 1) % 2
            elif (received_packet.seqno != seqno):
                client.my_socket.send(ack_packet.pack())

        self.write_file(self.recv_pkt_list) # write received file.


    def write_file(self, pkt_list):
        file = open('dl_gbn_' + str(self.requested_filename), 'wb')
        for pkt in pkt_list:
            file.write(pkt.data)
        print('File Written!')

    def recv_stop_and_wait(self):
        seqno = 0
        file = open('dl_sw_'+str(self.requested_filename),'w')
        while True:

            received_pack , addr = client.my_socket.recvfrom(600)
            received_packet = packet(pkd_data=received_pack)
            if(received_packet.checksum==structures.calc_checksum(received_packet.data) and received_packet.seqno==seqno):
                print(received_packet.data)
                file.write(received_packet.data)
                ack_packet = structures.ack(seqno= seqno,checksum=received_packet.checksum)
                client.my_socket.send(ack_packet.pack())
                seqno=(seqno+1)%2
            elif(received_packet.seqno!= seqno):
                client.my_socket.send(ack_packet.pack())

    def recv(self, algorithm,params=[]):
        recv_call = getattr(self,'recv_'+algorithm)
        if recv_call:
            recv_call(*params)
        else:
            print("error.. no such algorithm")



client = Client('client.in')
client.send_request()
received_pack , addr = client.my_socket.recvfrom(600)
received_packet = packet(pkd_data=received_pack)
server_new_port = int(received_packet.data)
print('New port number: ',server_new_port)
client.my_socket.connect((client.server_ip,server_new_port))
pkt,adr = client.my_socket.recvfrom(600)
pkt = packet(pkd_data=pkt,type='bytes')
recv_algo = str(pkt.data.decode()).split('.')[1]
print('Receiving using: ',recv_algo)
client.recv(recv_algo)
client.my_socket.close()

#client.recv_selective_repeat(5)


# seqno = 0
# while True:
#
#     received_pack , addr = client.my_socket.recvfrom(600)
#     received_packet = packet(pkd_data=received_pack)
#     if(received_packet.checksum==structures.calc_checksum(received_packet.data) and received_packet.seqno==seqno):
#         print(received_packet.data)
#         ack_packet = structures.ack(seqno= seqno,checksum=received_packet.checksum)
#         client.my_socket.send(ack_packet.pack())
#         seqno=(seqno+1)%2
#     elif(received_packet.seqno!= seqno):
#         client.my_socket.send(ack_packet.pack())

# client.recv_go_back_n()
# client.write_file(client.recv_pkt_list)


