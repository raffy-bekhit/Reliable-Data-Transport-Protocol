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
import threading
import socket

packet_size = 500
time_out = 5.0


class algorithms(enum.Enum):
    stop_and_wait = 0
    go_back_n=1
    selective_repeat = 2


def arrange_seqno(seqnos,base):

    temp1 = []
    temp2 = []
    seqnos.sort()
    for i in seqnos:
        if(i>=base):
            temp1.append(i)
        else:
            temp2.append(i)

    return temp1+temp2


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

def send_window_size(server_socket, window_size,client_addr):
    pkt = packet(data=str(window_size))
    server_socket.sendto(pkt.pack(),client_addr)
    ack, add = server_socket.recvfrom(600)
    ack_p = packet(pkd_data=ack, type='ack')
    if ack_p.checksum == calc_checksum(str(window_size)):
        print('Received file window size ack...')


def selective_repeat(server_socket,filename,client_addr):
    print('Sending using selective reapeat.')
    send_file_len(server_socket,client_addr,filename)
    send_window_size(server_socket,window_size,client_addr)
    file_content = readfile(filename)#string containing file content
    packet_number = 0;
    buffer = "" #divides file content into chunks of packet size
    seqno = 0
    send = True

    lost_list = lost_packets(len(file_content) // packet_size, probability, random_seed)
    my_threads=[]
    window = []
    received_acks = []
    total_packets = len(file_content) / packet_size
    lock = threading.Lock()
    send_base = 0
    already_acked = [] #seqno
    not_yet_acked = []
    lose = True
    counter = 0
    while True:
        while (packet_number < total_packets and len(window)<window_size): #fills window
            start_index = packet_number * packet_size
            end_index = packet_number * packet_size + packet_size
            if (end_index < len(file_content)):
                buffer = file_content[start_index:end_index]
            else:
                buffer = file_content[start_index:]

            send_packet = structures.packet(seqno=seqno, data=buffer)
            packed_packet = send_packet.pack()

            window.append(send_packet)
            not_yet_acked.append(send_packet)

            seqno=(seqno+1)%window_size
            packet_number=packet_number+1

        not_yet_acked.sort()
        my_threads = []

        for i in window:
            if(not (i.seqno in already_acked)):
                if(lose == False or len(lost_list)==0 or counter!=lost_list[0]%window_size):

                    server_socket.sendto(i.pack(), client_addr)
                    counter=counter+1
                    my_threads.append(threading.Thread(target=receive_ack,args=(server_socket,lock,received_acks)))
                    my_threads[-1].start()
                else:
                    lost_list.pop(0)
                    lose = False

        for thread in my_threads:
            thread.join()

        lose = True
        my_threads=[]
        received_acks.sort()

        i=0
        j=0

        while(len(received_acks)>j and len(not_yet_acked)>i):
            if(received_acks[j].seqno == not_yet_acked[i].seqno):
                if(received_acks[j].checksum == not_yet_acked[i].checksum):
                    already_acked.append(received_acks[j].seqno)
                    not_yet_acked.pop(i)
                j = j + 1
            elif(received_acks[j].seqno>not_yet_acked[i].seqno):
                i=i+1
            else:
                j=j+1

        already_acked = arrange_seqno(already_acked,send_base)
        received_acks=[]
        while(len(already_acked)>0):
            if(len(window)>0 and already_acked[0]==window[0].seqno):
                window.pop(0)
                send_base=(already_acked[0]+1)%window_size
                already_acked.pop(0)
            else:
                break


def receive_ack(socket,lock,received_acks):
    "used for selective repeat"

    lock.acquire(blocking=True)
    try:
        packed_data,addr = socket.recvfrom(600)
    except Exception:
        lock.release()
        return
    a = ack(pkd_data=packed_data)
    received_acks.append(a)
    lock.release()
    return


def stop_and_wait(server_socket,filename,client_addr):
    send_file_len(server_socket,client_addr,filename)
    print('Sending using stop and wait.')

    file_content = readfile(filename)
    packet_number =  0 ;
    buffer= ""
    seqno = 0
    send = True
    lost_list = lost_packets(len(file_content)//packet_size , probability , random_seed)

    while(packet_number<len(file_content)/packet_size):

        if(len(lost_list)>0 and packet_number==int(lost_list[0])):
            lost_list.pop(0)
            send = False
        if(send):
            send=False
            start_index = packet_number*packet_size
            end_index = packet_number * packet_size + packet_size
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


def send_file_len(socket, address, data):
    print('Required file: ' + str(data))
    req_file = str(data)
    pkts = get_packets_from_file(req_file)
    file_len = len(pkts)
    pkt = packet(seqno=0, data=((str(file_len)).encode()),type='bytes').pack_bytes()
    socket.sendto(pkt, address)
    while True:
        try:
            ack, add = socket.recvfrom(600)
            ack_p = packet(pkd_data=ack, type='ack')
            if ack_p.checksum == calc_checksum(str(file_len)):
                print('Received file length ack...')
                break
        except socket.timeout:
            continue


def go_back_n(file_name, server_socket, client_address, window_size=5):
    print('Sending using go back n.')
    pkt_list = get_packets_from_file(file_name) # converts file into packets.
    send_file_len(server_socket,client_address,file_name) # sends required file length to client(packets)

    flag = False
    i = 0
    #server_socket.settimeout(5)
    lost_pkts = lost_packets(len(pkt_list), probability, random_seed) # lost packets seqno
    while i < len(pkt_list):
        current_pkt = pkt_list[i:window_size+i] # current packets in window
        if window_size+i > len(pkt_list):
            current_pkt = pkt_list[i:]
        for pkt in current_pkt: # send all packets in window
            send = True
            if pkt.seqno in lost_pkts: # if packet to is lost, don't send.
                send = False
                lost_pkts.remove(pkt.seqno)
            if send:
                print('Sending packet # ', pkt.seqno)
                pkd_packet = pkt.pack_bytes()
                server_socket.sendto(pkd_packet,client_address)
            if flag is True and not send:
                flag = False
                break
        for pkt in current_pkt: # receive acks for sent pacekts in window
            try:
                ack_pkt = server_socket.recv(600)
                unpkd_ack = ack(pkd_data=ack_pkt)
                if unpkd_ack.checksum == pkt.checksum: # if ack received and not corrupted, increment current_pkt
                    i += 1
                    print('Ack# ' + str(unpkd_ack.seqno) + ' received')
                else:
                    print('Ack# ', unpkd_ack.seqno,' is corrupted..') # else, go back n.
                    flag = True
                    break
            except socket.timeout as e: # if an ack times out, go back n.
                send = True
                print('Ack # '+str(pkt.seqno)+' ack has timed out....resending packet')
                break


def send_requested_file(client_addr,serving_port,filename,algorithm_number=algorithms.stop_and_wait):
    sending_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #create new socket for client for sending
    sending_socket.bind((host,serving_port))
    sending_socket.settimeout(time_out)
    print('Client: '+str(client_addr[1])+' connected... sending file.')
    # send algorithm used to client to receive according to it.
    sending_socket.sendto(packet(data=(str(algorithm_number)).encode(),type='bytes').pack_bytes(),client_addr)
    if algorithm_number == algorithms.selective_repeat:
        selective_repeat(sending_socket,filename,client_addr)
    elif algorithm_number == algorithms.go_back_n:
        go_back_n(filename,sending_socket,client_addr)
    else:
        stop_and_wait(sending_socket,filename,client_addr)



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

req_err = True
while True:
    print('Waiting for connection... ')
    request_data, addr = s.recvfrom(1024)    # receives packet from clients
    pkt = packet(pkd_data=request_data)
    if req_err:
        req_err = False
        pkt.checksum=pkt.checksum-10
    if pkt.checksum == calc_checksum(pkt.data):
        ack_pkt = ack(seqno=0, checksum=calc_checksum(pkt.data))
        s.sendto(ack_pkt.pack(),addr)
        print('File request received, sending ack..')
    else:
        print('File request Corrupted..')
        continue

    if(addr not in clients): # keep track of clients
        clients.append(addr)

    while serving_port in used_ports: # searching for a free port
        serving_port=serving_port-1
        if(serving_port<1024):
            serving_port=49151
    used_ports.append(serving_port)
    s.sendto(packet(data=str(serving_port), seqno=0).pack(),addr)

    pid = os.fork()  # fork a new process for the client
    if pid == 0:
        request_packet = structures.packet(pkd_data=request_data)  # create a request packet from received data
        send_requested_file(addr,serving_port,request_packet.data,algorithms.selective_repeat)
        # send using the algorithm specified
        print('File Sent..')
        os.kill(os.getpid(),0)