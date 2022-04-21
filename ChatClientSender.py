import argparse
import time
from socket import *

# CONSTANTS
PAYLOAD = 1500                      # size of UDP payload, without headers
TIMEOUT = 1                         # retransmission time in seconds
TYPE_DATA = 2                       # This will be a header in the message packet
TYPE_ACK = 3                        # This will be a header in the message packet

# Handle command line arguments
# python3 ChatClientSender.py -s server_name -p port_number -t filename1 filename2
def set_command_line_args():
    global __server_addr, __local_file, __transfer_loc

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--Server", help = "Server Name")
    parser.add_argument("-p", "--Port", help = "Server Port")
    parser.add_argument("-t", "--Tag", nargs='+', help = "Filenames")

    args = parser.parse_args()

    server_name = args.Server if args.Server else 'date.cs.umass.edu'
    server_port = args.Port if args.Port else 8888
    __server_addr = (server_name, server_port)
    __local_file = args.Tag[0] if args.Tag else 'stdin'
    __transfer_loc = args.Tag[1] if args.tag else 'stdout'


# Setting up UDP
def create_udp_socket():
    # NOTE: Max size 2048 bytes can send
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Setting up connection with Message Server
def connect_to_relay_server(socket):
    name_command = "NAME aacastilloSender"
    relay_command = "CONN aacastilloReciever"

    send_name_command(name_command, socket)
    send_relay_command(relay_command, socket)

# NOTE: have to use the ". " command to exit relay mode, Use Quit command to clear control commands, and exit gracefully
def send_name_command(command, socket):
    global TIMEOUT, __server_addr
    socket.settimeout(TIMEOUT)
    socket.sendto(command.encode(), __server_addr)

    try:
        response, server = socket.recvfrom(2048)
        print("[INFO] relay server response to command is: %s", response.decode())
        if (response.decode() != "OK Hello aacastilloSender"):
            print("[ERROR] Incorrect response from server, retrying NAME_command")
            send_name_command(command, socket)
    except socket.timeout:
        print("[INFO] Retrying sending NAME_command to relay server")
        send_name_command(command, socket)

    socket.settimeout(None)
    print("[INFO] Successful name command sent and correct response recieved")


def send_relay_command(command, socket):
    global TIMEOUT, __server_addr
    socket.settimeout(TIMEOUT)
    socket.sendto(command.encode(), __server_addr)

    try:
        response, server = socket.recvfrom(2048)
        print("[INFO] relay server response to command is: %s", response.decode())
        if ("OK Relaying to aacastilloReciever" not in response.decode()):
            print("[ERROR] Incorrect response from server, retrying RELAY_command")
            send_name_command(command, socket)
    except socket.timeout:
        print("[INFO] Retrying sending RELAY_command to relay server")
        send_name_command(command, socket)

    socket.settimeout(None)
    print("[INFO] Successful name command sent and correct response recieved")

# get_data() => data[] of size 1500
def get_data():
    global __local_file, PAYLOAD
    if __local_file == "stdin":
        data = input('Input message:')
    else:
        data = open(__local_file)
    data_arr = [data[i:i+PAYLOAD] for i in range(0,len(data), PAYLOAD)]
    print("[INFO] Data array: ", data_arr)
    return data_arr

def rdt_send_all(data_arr):
    while data_arr:
        data = data_arr.pop(0)
        #CAUTION: encode() is for strings, do you need this for fiel data?
        rdt_send(data.encode())

def rdt_send(data):
    
    #If file is default StdIn
        #Take input message from standard input
        #Break down string into an array of messages with chunk length 1500
        #let seq = 0
        #while len(array) != 0:
            # if seq==0
                # rdt_send(data)
                    # if len(array) = 1, set finalflag = 1
                    # pkt = make_pkt(checksum, sequence, finalflag, data)
                    # udt_send(pkt)
                    # start_timer
                    # wait for Ack0
                        # rcv_pkt, if corrupt(rcv_pkt) || isAck(rcv_pkt, (seq+1)%2)
                        # if notcorrupt(rcv_pkt) && isAck(rcvPkt)
                            # stop timeout
                            # Set seq = 1
                        # if timeout, udt_send(pkt) again, restart timeout again
            # if seq==1
                # rdt_send(data)
                    # pkt = make_pkt(checksum, sequence, finalflag, data)
                    # udt_send(pkt)
                    # start_timer
                    # wait for Ack0
                        # rcv_pkt, if corrupt(rcv_pkt) || isAck(rcv_pkt, (seq+1)%2)
                        # if notcorrupt(rcv_pkt) && isAck(rcvPkt)
                            # stop timeout
                            # Set seq = 1
                        # if timeout, udt_send(pkt) again, restart timeout again

    # If file is local filename
        #Get local file from directory
        #break down file into array of bytes with chunk length 1500
        #repeat
    # Note: How to make checksum



# from socket import *
# serverName = 'localhost'
# serverPort = 12000
# clientSocket = socket(AF_INET, SOCK_DGRAM)
# message = input('Input lowercase sentence:')
# clientSocket.sendto(message.encode(),(serverName, serverPort))
# modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# print (modifiedMessage.decode())
# clientSocket.close()