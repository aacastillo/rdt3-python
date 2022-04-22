from server_commands import *
from socket import *

TIMEOUT = 1

def send_command(socket, command):
    global TIMEOUT
    socket.settimeout(TIMEOUT)
    socket.sendto(command.encode(), ("date.cs.umass.edu", 8888))

    try:
        response, server = socket.recvfrom(2048)
        print("[INFO] relay server response:", response.decode())
    except:
        print("[TIMEOUT] Retrying command")
        send_command(socket, command)

    socket.settimeout(None)

def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    while True:
        command = input("Enter your command here: ")
        if command == "exit":
            break
        send_command(sock, command)

main()