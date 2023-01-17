#!/usr/bin/env python3
import socket, sys
import time
from multiprocessing import Process

# define address & buffer size
HOST = ""
PORT = 8001
PORT_END = 80
BUFFER_SIZE = 1024

# create a tcp socket
def create_tcp_socket():
    print('Creating socket')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        msg = e.msg
        print(f'Failed to create socket. Error code: {str(msg[0])} , Error message : {msg[1]}')
        sys.exit()
    print('Socket created successfully')
    return s


# get host information
def get_remote_ip(host):
    print(f'Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()

    print(f'Ip address of {host} is {remote_ip}')
    return remote_ip


# send data to server
def send_data(serversocket, payload):
    print("Sending payload")
    try:
        serversocket.sendall(payload.encode())
    except socket.error:
        print('Send failed')
        sys.exit()
    print("Payload sent successfully")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_front:
        proxy_front.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        proxy_front.bind((HOST, PORT))
        proxy_front.listen(2)

        while True:
            conn, addr = proxy_front.accept()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end:
                remote_ip = get_remote_ip('www.google.com')
                proxy_end.connect((remote_ip, PORT_END))
                p = Process(target=handle_request, args=(conn, addr, proxy_end), daemon=True)
                p.start()


def handle_request(conn, addr, proxy_end):
    print(f'Connected by address: {addr}')
    client_request_data = conn.recv(BUFFER_SIZE)
    proxy_end.sendall(client_request_data)

    proxy_end_response = b''
    while True:
        data = proxy_end.recv(BUFFER_SIZE)
        if not data:
            break
        proxy_end_response += data
    conn.sendall(proxy_end_response)
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


if __name__ == "__main__":
    main()
