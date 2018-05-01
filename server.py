import signal
import socket               # Import socket module
import os
import structures
from structures import packet
import time
import multiprocessing
import enum
from structures import packet,ack, calc_checksum
import random
from socket import timeout


packet_size = 500


class algorithms(enum.Enum):
    stop_and_wait = 0
    go_back_n=1
    selevtive_repeat = 2




def lost_packets(total_packets,probability,seed):
    "returns list of random packets to be lost for simulation"
    random.seed(seed)
    list = random.sample(range(total_packets),int(probability*total_packets))
    list = [int(i) for i in list]
    list.sort()
    return list

def readfile(filename):
    "returns content of file as string"
    file = open(filename, 'r')
    file_content = file.read()
    file.close()
    return file_content

def selective_repeat(server_socket,filename,client_addr):
    file_content = readfile(filename)#string containing file content
    packet_number = 0;
    buffer = "" #divides file content into chunks of packet size
    seqno = 0
    send = True
    server_socket.settimeout(5.0) #sets timeou
    lost_list = lost_packets(len(file_content) // packet_size, probability, random_seed)
    window = []

    total_packets = len(file_content) / packet_size

    while (packet_number < total_packets and len(window)<window_size): #fills window
        start_index = packet_number * packet_size
        end_index = packet_number * packet_size + packet_size - 1
        if (end_index < len(file_content)):
            buffer = file_content[start_index:end_index]
        else:
            buffer = file_content[start_index:]

        send_packet = structures.packet(seqno=seqno, data=buffer)
        packed_packet = send_packet.pack()

        window.append(packed_packet)


        seqno=seqno+1
        packet_number=packet_number+1

    for i in window:
        server_socket.sendto(i, client_addr)




def send_stop_wait(server_socket,filename,client_addr):
    file_content = readfile(filename)
    packet_number =  0 ;
    buffer= ""
    seqno = 0
    send = True
    server_socket.settimeout(5.0)

    lost_list = lost_packets(len(file_content)//packet_size , probability , random_seed)

    while(packet_number<len(file_content)/packet_size):
        

        if(len(lost_list)>0 and packet_number==int(lost_list[0])):
            lost_list.pop(0)
            send = False
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


        except timeout:
            send=True #resend
            continue

        ack__packet = structures.ack(pkd_data=ack_pack)

        if(ack__packet.checksum==send_packet.checksum and ack__packet.seqno==seqno):
            packet_number = packet_number + 1
            seqno=(seqno+1)%2
            send=True


def get_bytes_from_file(file_name):
    return open(file_name, 'rb').read()


def get_packets_from_file(file_name):
    file_bytes = get_bytes_from_file(file_name)
    file_length = len(file_bytes)
    seq_count = 0
    pkt_list = []
    for i in range(0, file_length, 500):
        if i + 500 > file_length:
            pkt = packet(seqno=seq_count, data=file_bytes[i:], type='bytes')
        else:
            pkt = packet(seqno=seq_count, data=file_bytes[i:i + 500], type= 'bytes')
        pkt_list.append(pkt)
        seq_count += 1
    return pkt_list

def send_file_len(socket, address, data,file_len):

    print('Required file: ' + str(data))
    req_file = str(data)
    get_packets_from_file(req_file)
    pkt = packet(seqno=0, data=((str(file_len)).encode()),type='bytes').pack_bytes()
    socket.sendto(pkt, address)
    ack, add = socket.recvfrom(600)
    ack_p = packet(pkd_data=ack, type='ack')
    if ack_p.checksum == calc_checksum(str(file_len)):
        print('Received file length ack...')


def go_back_n(file_name, server_socket, client_address, window_size=5):
    pkt_list = get_packets_from_file(file_name)
    send_file_len(server_socket,client_address,file_name,len(pkt_list))
    flag = False
    i = 0
    while i < len(pkt_list):
        current_pkt = pkt_list[i:window_size+i]
        if window_size+i > len(pkt_list):
            current_pkt = pkt_list[i:]
        for pkt in current_pkt:
            pkd_packet = pkt.pack_bytes()
            server_socket.sendto(pkd_packet,client_address)
            if flag is True:
                flag = False
                break
        for pkt in current_pkt:
            try:
                ack_pkt = server_socket.recv(600)
                unpkd_ack = ack(pkd_data=ack_pkt)
                if unpkd_ack.checksum == pkt.checksum:
                    i += 1
                    print('Ack# ' + str(unpkd_ack.seqno) + ' received')
                else:
                    print('Ack# ', unpkd_ack.seqno,' is corrupted/delayed..')
                    flag = True
                    break
            except socket.timeout as e:
                print('Ack # '+str(pkt.seqno)+' ack has timed out....resending')
                break


def send_requested_file(client_addr,serving_port,filename,algorithm_number=algorithms.stop_and_wait):
    sending_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sending_socket.bind((host,serving_port))
    print('Client: '+str(client_addr[1])+' connected... sending file.')
    #sending_socket.sendto(packet(data=str(serving_port),seqno=0).pack(),client_addr)
    send_stop_wait(sending_socket,filename,client_addr)
    # go_back_n(filename,sending_socket,client_addr)


s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Create a socket object (udp)
host = '127.0.0.1' # localhost ip

file = open('server.in','r') # open file containing data about server
port = int(file.readline())
window_size = int(file.readline()) # in datagrams
random_seed = int(file.readline())
probability = float(file.readline())


s.bind((host, port))        # Bind to the port
#s.setblocking(1)
clients = []  # list of online clients


serving_port = 49151  # port used to send the file
used_ports=[]  # list of ports used to send the file


while True:
    print('Waiting for connection... ')
    request_data, addr = s.recvfrom(1024)    # receives packet from clients


    if(addr not in clients): #keep track of clients
        clients.append(addr)


    while serving_port in used_ports: #searching for a free port
        serving_port=serving_port-1
        if(serving_port<1024):
            serving_port=49151
    used_ports.append(serving_port)
    s.sendto(packet(data=str(serving_port), seqno=0).pack(),addr)
   # pid = os.fork() #fork a new process for the client


   # if(pid == 0):

    request_packet = structures.packet(pkd_data=request_data) #create a request packet from received data
       #send_stop_wait(s, request_packet.data,addr)
    send_requested_file(addr,serving_port,request_packet.data,algorithms.stop_and_wait)
    os.kill(os.getpid(),0)