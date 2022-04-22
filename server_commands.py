import traceback, time

TIMEOUT = 1

#Setting up connection with Message Server
def connect_to_relay_server(socket, server_addr2, whoami):
    global server_addr
    server_addr = server_addr2

    target = None
    if whoami == "Receiver":
        target = "Sender"
    else:
        target = "Receiver"

    send_name_command("NAME aacastillo", whoami, socket)
    wait_for_target(socket, target)
    send_relay_command("CONN aacastillo", target, socket)

# NOTE: have to use the ". " command to exit relay mode, Use Quit command to clear control commands, and exit gracefully
def send_name_command(command, whoami, socket):
    global TIMEOUT, server_addr
    socket.settimeout(TIMEOUT)
    command = command+whoami
    # print("[TEST] ", server_addr, command)
    socket.sendto(command.encode(), server_addr)

    try:
        response, server = socket.recvfrom(2048)
        # print("[INFO] relay server response to command is:", response.decode())
        if ("OK Hello aacastillo"+whoami not in response.decode()):
            # print("[ERROR] Incorrect response from server, retrying NAME_command")
            send_name_command(command, whoami, socket)
    # except socket.timeout:
    #     # print("[TIMEOUT] Retrying sending NAME_command to relay server")
    #     send_name_command(command, whoami, socket)
    # except UnicodeDecodeError:
    #     # print("[UNICODE ERR]")
    #     send_name_command(command, whoami, socket)
    except:
        # traceback.print_exc()
        send_name_command(command, whoami, socket)

    socket.settimeout(None)
    # print("[SUCCESS] Successful NAME command sent and correct response received")

def wait_for_target(socket, target):
    global TIMEOUT, server_addr

    time.sleep(2)
    socket.settimeout(TIMEOUT)
    socket.sendto("LIST".encode(), server_addr)

    try:
        response, server = socket.recvfrom(2048)
        # print("[RESPONSE] response: %s, target: %s" % (response.decode(), target))
        if (("aacastillo"+target) not in response.decode()):
            # print("[OFFLINE] waiting for %s to get online" % (target,))
            wait_for_target(socket, target)
        else:
            # print("[ONLINE] %s online, starting relay" % (target,))
            return
    # except socket.timeout:
    #     # print("[TIMEOUT] Retry WAIT Command")
    #     wait_for_target(socket, target)
    # except UnicodeDecodeError:
    #     # print("[UNICODE ERR]")
    #     wait_for_target(socket, target)
    except:
        # traceback.print_exc()
        wait_for_target(socket, target)

def send_relay_command(command, target, socket):
    global TIMEOUT, server_addr
    socket.settimeout(TIMEOUT)
    socket.sendto((command+target).encode(), server_addr)

    try:
        response, server = socket.recvfrom(2048)
        # print("[INFO] relay server response to command is:", response.decode())
        if ("who is probably offline" in response.decode()):
            # print("[OFFLINE] waiting for Receiver to get online")
            send_relay_command(command, target, socket)
        if ("OK Relaying to aacastillo"+target not in response.decode()):
            # print("[ERROR] Incorrect response from server, retrying RELAY_command")
            send_relay_command(command, target, socket)
    # except socket.timeout:
    #     # print("[TIMEOUT] Retrying sending RELAY_command to relay server")
    #     send_relay_command(command, target, socket)
    # except UnicodeDecodeError:
    #     # print("[UNICODE ERR]")
    #     send_relay_command(command, target, socket)
    except:
        # traceback.print_exc()
        send_relay_command(command, target, socket)

    socket.settimeout(None)
    # print("[SUCCESS] Successful RELAY command sent and correct response received")

def send_command(socket, command):
    global TIMEOUT, server_addr

    socket.settimeout(TIMEOUT)
    socket.sendto(command.encode(), server_addr)

    try:
        response, server = socket.recvfrom(2048)
        # print("[INFO] relay server response to command: ", response.decode())
    # except socket.timeout:
    #     # print("[TIMEOUT] Retrying command")
    #     send_command(socket, command)
    # except UnicodeDecodeError:
    #     # print("[UNICODE ERR]")
    #     send_command(socket, command)
    except:
        # traceback.print_exc()
        send_command(socket, command)

    socket.settimeout(None)

def exit_server(socket):
    send_command(socket, ". ")
    send_command(socket, "QUIT")
