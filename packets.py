from socket import *
import pickle, hashlib, time

# Setting up UDP
def create_udp_socket():
    # NOTE: Max size 2048 bytes can send
    return socket(AF_INET, SOCK_DGRAM)

def is_correct_checksum(pkt):
    pkt_checksum = pkt[0]
    del pkt[0]

    _hash = hashlib.sha256()
    _hash.update(pickle.dumps(pkt))
    cur_checksum = _hash.digest()

    if cur_checksum == pkt_checksum:
        # print("[MATCH] Correct checksum match, seq_num: %d, finalflag: %d" % (pkt[0], pkt[1]))
        ## print("[MATCH] pkt hash, calc_hash", pkt_checksum, cur_checksum)
        return True
    else:
        return False

def make_sender_packet(seq_num, final_flag, transfer_loc, data):
    #Checksum (32), seq_num, final_flag, and data
    send_pkt = [seq_num, final_flag, transfer_loc, data]
    ## print("[DATA] seq: %d, len: %d, data: " % (seq_num,len(data)), data)
    serial_pkt = pickle.dumps(send_pkt)
    checksum = hashlib.sha256()
    checksum.update(serial_pkt)
    send_pkt.insert(0, checksum.digest())
    serial_pkt = pickle.dumps(send_pkt)
    return serial_pkt

def make_receiver_packet(ack_seq_num, final_flag):
    #Checksum (32), seq_num, final_flag
    send_pkt = [ack_seq_num, final_flag]
    serial_pkt = pickle.dumps(send_pkt)
    checksum = hashlib.sha256()
    checksum.update(serial_pkt)
    send_pkt.insert(0, checksum.digest())
    serial_pkt = pickle.dumps(send_pkt)
    return serial_pkt

def set_window_size(num_packets,send_base):
    window = min(14, num_packets-send_base)
    # # print("[WINDOW] new window size: %d" %(window,))
    return window