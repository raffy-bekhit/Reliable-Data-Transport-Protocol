import signal
import socket               # Import socket module
import os
import structures
from structures import packet
import time
import multiprocessing
import enum
from structures import packet

packet_size = 500


class algorithms(enum.Enum):
    stop_and_wait = 0
    go_back_n=1
    selevtive_repeat = 2

acks = {}




def send_stop_wait(server_socket,filename,client_addr):
    file = open(filename,'r')
    file_content = file.read()
    packet_number =  0 ;
    buffer= ""
    seqno = 0
    send = True
    server_socket.settimeout(30.0)
    while(packet_number<len(file_content)/packet_size):
        

        if(send):
            send=False
            start_index = packet_number*packet_size
            end_index = packet_number * packet_size + packet_size - 1
            if(end_index<len(file_content)):
                buffer = file_content[start_index:end_index]
            else:
                buffer = file_content[start_index:]

            send_packet = structures.packet(seqno=seqno,data=buffer)
            packed_packet = send_packet.pack()
            server_socket.sendto(packed_packet,client_addr)

        try:
            ack_pack , addr = server_socket.recvfrom(600)


        except TimeoutError:
            send=True #resend
            continue

        ack__packet = structures.ack(pkd_data=ack_pack)

        if(ack__packet.checksum==send_packet.checksum and ack__packet.seqno==seqno):
            packet_number = packet_number + 1
            seqno=(seqno+1)%2
            send=True







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

def send_requested_file(client_addr,serving_port,filename,algorithm_number=algorithms.stop_and_wait):
    sending_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sending_socket.bind((host,serving_port))

    #sending_socket.sendto(packet(data=str(serving_port),seqno=0).pack(),client_addr)
    send_stop_wait(sending_socket,filename,client_addr)




s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Create a socket object (udp)
host = '127.0.0.1' # localhost ip

file = open('server.in','r') #open file containing data about server
port = int(file.readline())
window_size = int(file.readline()) #in datagrams
random_seed = int(file.readline())
probability = float(file.readline())


s.bind((host, port))        # Bind to the port
#s.setblocking(1)
clients = [] #list of online clients


serving_port = 49151 #port used to send the file
used_ports=[] #list of ports used to send the file


while True:

    request_data, addr = s.recvfrom(1024)    # receives packet from clients


    if(addr not in clients): #keep track of clients
        clients.append(addr)


    while serving_port in used_ports: #searching for a free port
        serving_port=serving_port-1
        if(serving_port<1024):
            serving_port=49151
    used_ports.append(serving_port)
    s.sendto(packet(data=str(serving_port), seqno=0).pack(),addr)
    pid = os.fork() #fork a new process for the client


    if(pid == 0):

        request_packet = structures.packet(pkd_data=request_data) #create a request packet from received data
        #send_stop_wait(s, request_packet.data,addr)

        send_requested_file(addr,serving_port,request_packet.data,algorithms.stop_and_wait)
        os.kill(os.getpid(),0)