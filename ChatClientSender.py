import argparse, time, pickle, _thread, traceback
from socket import *
from server_commands import *
from packets import *

# CONSTANTS
PAYLOAD = 1900
TIMEOUT = 1
STOPPED_TIME = -1
SLEEP = 0.1

# Handle command line arguments
# python ChatClientSender.py -t redsox.jpg redsox2.jpg
# python ChatClientSender.py -s server_name -p port_number -t filename1 filename2
def set_command_line_args():
    global server_addr, local_file, transfer_loc

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--Server", help = "Server Name")
    parser.add_argument("-p", "--Port", help = "Server Port")
    parser.add_argument("-t", "--Tag", nargs='+', help = "Filenames")

    args = parser.parse_args()

    server_name = args.Server if args.Server else 'date.cs.umass.edu'
    server_port = int(args.Port) if args.Port else 8888
    server_addr = (server_name, server_port)
    local_file = args.Tag[0] if args.Tag else 'stdin'
    transfer_loc = args.Tag[1] if args.Tag else 'stdout'

# get_packets() => packets[]
# NOTE: Packet: [checksum, seq_num, final_flag, file_location, data]
def get_packets():
    global local_file, PAYLOAD, transfer_loc
    
    packets = []
    seq_num = 0

    if local_file == "stdin":
        file = open("__stdin__", w)
        data = input('Input message:')
        file.write(data)
        file.close()
        file = open("__stdin__", "rb")
    else:
        file = open(local_file, "rb")
    
    while True:
        data = file.read(PAYLOAD)
        if not data:
            break
        packets.append(make_sender_packet(seq_num, 0, transfer_loc, data)) 
        seq_num += 1
    
    file.close()

    #NOTE: Empty packet with final flag, so receiver knows its the last packet
    packets.append(make_sender_packet(seq_num, 1, transfer_loc, b'')) 

    # print("[SERIAL_PKT] Serialized packets list")
    return packets

def rdt_gbn_send(packets, socket):
    global mutex, send_base, server_addr, send_base_timer, TIMEOUT, STOPPED_TIME, SLEEP

    mutex = _thread.allocate_lock()
    send_base = 0
    next_seq_num = 0
    send_base_timer = STOPPED_TIME
    window_size = set_window_size(len(packets), send_base)
    
    _thread.start_new_thread(rdt_gbn_receive, (socket,))
    
    while send_base < len(packets):
        mutex.acquire()

        window_size = set_window_size(len(packets), send_base)

        # Send all the packets in the window
        # print("[PACKETS] sending all packets with next_seq: %d, base: %d and window: %d and num_packets: %d" % (next_seq_num, send_base, window_size, len(packets)))
        while next_seq_num < send_base + window_size:
            socket.sendto(packets[next_seq_num], server_addr)
            next_seq_num += 1

        # Start timer for send_base
        if send_base_timer == STOPPED_TIME:
            # print("[TIMER] Starting send base timer")
            send_base_timer = time.time()

        while send_base_timer != STOPPED_TIME and time.time() - send_base_timer < TIMEOUT:
            mutex.release()
            # # print("[SLEEP]")
            time.sleep(SLEEP)
            mutex.acquire()

        if send_base_timer == STOPPED_TIME:
            window_size = set_window_size(len(packets), send_base)
            # print("[ACK/WINDOW] received ACK(s), shifting window: %d" %(window_size,))
        if time.time()-send_base_timer >= TIMEOUT: # Timeout occured
            send_base_timer = STOPPED_TIME
            next_seq_num = send_base # restart send of entire window
            # print("[TIMEOUT] Send base packet timeout occured, next_seq: %d" %(next_seq_num,))        
        
        mutex.release()

def rdt_gbn_receive(socket):
    global mutex, send_base, send_base_timer, STOPPED_TIME

    while True:
        serial_pkt, server = socket.recvfrom(2048)
        pkt = []
        try:
            pkt = pickle.loads(serial_pkt)
            # NOTE: Packet: [checksum, seq_num, final_flag, data]
            if is_correct_checksum(pkt):
                ack_seq_num = pkt[0]
                final_flag = pkt[1]

                mutex.acquire()
                send_base = ack_seq_num + 1
                send_base_timer = STOPPED_TIME
                # print("[ACK] receiver has ACK: %d, final flag: %d, time: %f, and updated base: %d" % (ack_seq_num, final_flag, time.time(), send_base))
                mutex.release()

                if final_flag:
                    # print("[END] final flag received")
                    break
        except pickle.UnpicklingError:
            # print("[PICKLE] pickle corruped")
            pass
        except:
            traceback.print_exc()
    exit_server(socket)

def main():
    global server_addr
    set_command_line_args()
    socket = create_udp_socket()
    try:
        connect_to_relay_server(socket, server_addr, "Sender")
        packets = get_packets()
        rdt_gbn_send(packets, socket)
    except:
        traceback.print_exc()
        exit_server(socket)
    exit_server(socket)
    

main()