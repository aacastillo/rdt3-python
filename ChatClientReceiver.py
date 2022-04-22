import argparse, time, pickle, _thread, traceback
from socket import *
from packets import *
from server_commands import *

# CONSTANTS
PAYLOAD = 1900
TIMEOUT = 1
STOPPED_TIME = -1
SLEEP = 0.1

# Handle command line arguments
# python3 ChatClientSender.py -s server_name -p port_number -t filename1 filename2
def set_command_line_args():
    global server_addr

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--Server", help = "Server Name")
    parser.add_argument("-p", "--Port", help = "Server Port")

    args = parser.parse_args()

    server_name = args.Server if args.Server else 'date.cs.umass.edu'
    server_port = int(args.Port) if args.Port else 8888
    server_addr = (server_name, server_port)

def rdt_gbn_receive(socket):
    global server_addr, transfer_loc
    expected_seq_num = 0
    collected_data = dict() # {tran_loc: {seq: data}}

    while True:
        serial_pkt, _ = socket.recvfrom(2048)
        try:
            pkt = pickle.loads(serial_pkt)
            # # print("[TEST] pkt, ")
            # # print(pkt)
            if is_correct_checksum(pkt):
                seq_num = pkt[0]
                final_flag = pkt[1]
                transfer_loc = pkt[2]
                data = pkt[3]

                # print("[PACKET] received packet seq_num %d, final flag: %d, and transfer location: %s" % (seq_num, final_flag, transfer_loc))

                if seq_num == expected_seq_num:
                    serial_pkt = make_receiver_packet(expected_seq_num, final_flag)
                    socket.sendto(serial_pkt, server_addr)

                    if final_flag == 1:
                        for i in range(0,5):
                            socket.sendto(serial_pkt, server_addr)

                        # print("[END] final flag received")
                        break

                    if collected_data.get(transfer_loc) == None:
                        collected_data[transfer_loc] = dict()
                        collected_data[transfer_loc][seq_num] = data
                    else:
                        collected_data[transfer_loc][seq_num] = data

                    # print("[ACK_SEND] received expected data seq %d, sending back ACK: %d, and writing to %s, time: %f" % (expected_seq_num, expected_seq_num+1, transfer_loc, time.time()))
                    expected_seq_num += 1
                else:
                    serial_pkt = make_receiver_packet(expected_seq_num-1, 0)
                    socket.sendto(serial_pkt, server_addr)
                    # print("[RETRY] did not receive expected packet %d, final flag: %d" %(expected_seq_num, final_flag))
        except pickle.UnpicklingError:
            # print("[PICKLE] Error, ignore")
            pass
        except:
            traceback.print_exc()

    push_to_transfer_loc(collected_data)
    exit_server(socket)

def push_to_transfer_loc(collected_data):
    for location in collected_data:
        data_dict = collected_data[location]
        # # print(data_dict)
        
        data = data_dict[0]
        for seq in range(1, len(data_dict)):
            data += data_dict[seq]
        if location == "stdout":
            print(data)
        else:
            file = open(location, 'wb')
            file.write(data)
            file.close()

# except:
#     # print("[PICKLE] Corrupted")
#     pass

def main():
    global server_addr
    set_command_line_args()
    socket = create_udp_socket()

    try:
        connect_to_relay_server(socket, server_addr, "Receiver")
        rdt_gbn_receive(socket)
    except:
        traceback.print_exc()
        exit_server(socket)
    exit_server(socket)

main()