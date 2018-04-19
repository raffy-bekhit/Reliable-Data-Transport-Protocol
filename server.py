import signal
import socket               # Import socket module
import os
import structures
from structures import packet


packet_size = 500

def send_stop_wait(server_socket,filename):
    file = open(filename,'r')
    file_content = file.read()
    packet_number =  0 ;
    buffer= ""
    seqno = 0
    
    while(packet_number<len(file_content)/packet_size):
        start_index = packet_number*packet_size
        end_index = packet_number * packet_size + packet_size - 1
        if(end_index<len(file_content)):
            buffer = file_content[start_index:end_index]
        else:
            buffer = file_content[start_index:]

        my_packet = structures.packet(seqno=0,data=buffer)
        packed_packet = my_packet.pack()
        server_socket.sendto(packed_packet,addr)
        packet_number=packet_number+1


def get_bytes_from_file(file_name):
    return open(file_name,'rb').read()


def go_back_n(file_name,server_socket,client_address,windows_size):
    file_bytes = get_bytes_from_file(file_name)
    file_length = len(file_bytes)
    seq_count = 0
    pkt_list = []
    for i in range(0, file_length, 500):
        if i+500 > file_length:
            pkt = packet(seqno=seq_count,data=file_bytes[i:],type='bytes')
        else:
            pkt = packet(seqno=seq_count,data=file_bytes[i:i+500],type='bytes')
        pkt_list.append(pkt)
        seq_count += 1
    for i in range(0,len(pkt_list)):
        for w in range(i,window_size+i):
            pkt =pkt_list[w]
            pkd_packet = pkt.pack(type='bytes')
            server_socket.sendto(pkd_packet,client_address)
        for w in range(i,window_size+i):
            pkt = pkt_list[w]
            server_socket.settimeout(10)
            try:
                ack = server_socket.recvfrom(client_address)
                if ack.checksum == pkt.checksum:
                    i += 1
                else:
                    break
            except socket.timeout as e:
                print('Packet #'+str(pkt.seqno)+'has timed out....resending')
                break



s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Create a socket object
host = '127.0.0.1' # Get local machine name

file = open('server.in','r')
port = int(file.readline())
window_size = int(file.readline()) #in datagrams
random_seed = int(file.readline())
probability = float(file.readline())
connections_number = int(file.readline())

s.bind((host, port))        # Bind to the port

# s.recvfrom(connections_number) # Now wait for client connection.

while True:

    request_data, addr = s.recvfrom(600)    # Establish connection with client.

    pid = os.fork()

    if(pid == 0):
        if(len(request_data)>8):
            request_packet = structures.packet(pkd_data=request_data)
            send_stop_wait(s, request_packet.data)

        os.kill(os.getpid(),0)