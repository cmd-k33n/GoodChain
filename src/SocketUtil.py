"""
The SocketUtils module will provide the necessary networking functionality for the GoodChain project.

The SocketUtils module will provide the following functionality:
- Send Object
- Receive Object
- Open Listening Socket
- Open Sending Socket
- Open Listening Socket in a separate thread
- Send an object to all known nodes in separate threads

"""

import socket
import pickle
from threading import Thread
from queue import Queue

# Constants
NODE_IP = socket.gethostbyname('localhost')
HEADER_LEN = 64
FORMAT = 'utf-8'
SEND_TIMEOUT = 30
MAX_CONNECTIONS = 5
NODE_LISTENING_PORT = 5050
NODE_SENDING_PORT = 5060

# TODO: Since we will be working locally with multiple nodes we will actually need to manually set different ports for each node.
# TODO: change print statements to logging statements

LISTENING_PORTS = (5051, 5052, 5053, 5054)

CONFIRM_MSG = "Message received"
CONFIRM_MSG_LEN = len(CONFIRM_MSG.encode(FORMAT))

received_objects = Queue()


def start_listening_thread():
    # Spin a secondary thread for listening
    t = Thread(target=start_listening)
    t.start()


def start_listening():
    # Create the socket object
    s = open_listening_connection()

    while True:
        # Wait for the connection
        conn, addr = s.accept()
        print(f"[NEW CONNECTION] {addr[0]}:{addr[1]} connected.")

        # Spin a tertiary thread once there is a connection
        t = Thread(target=receive_object, args=(conn, addr))
        t.start()


def open_listening_connection(node_ip: str = NODE_IP, node_port: int = NODE_LISTENING_PORT) -> socket.socket:
    # Create the socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the IP and port
        s.bind((node_ip, node_port))

        # Listen for incoming connections
        s.listen(MAX_CONNECTIONS)

        print(f"[LISTENING] Node is listening on {node_ip}:{node_port}")
    except OSError as e:
        s.close()
        print(e)

    return s


def open_sending_connection(host: str, port: int) -> socket.socket:
    # Create the socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.settimeout(SEND_TIMEOUT)

    try:  # Connect to the server
        s.connect((host, port))
    except OSError as e:
        s.close()
        print(e)

    return s


def send_object(receiver_ip: str, receiver_port: int, obj: object):
    # Create the socket object
    s = open_sending_connection(receiver_ip, receiver_port)
    # prepare the object and header
    data = pickle.dumps(obj)
    data_size = len(data)
    header = str(data_size).encode(FORMAT)
    header += b' ' * (HEADER_LEN - len(header))

    print(f"[SENDING] {data_size} bytes to {receiver_ip}:{receiver_port}")
    s.sendall(header)  # send header
    s.sendall(data)  # send data

    print(s.recv(CONFIRM_MSG_LEN).decode(FORMAT))  # receive confirmation

    s.close()


def receive_object(conn: socket.socket, addr: tuple):
    # Receive the object
    header = conn.recv(HEADER_LEN).decode(FORMAT)  # receive header
    data_len = int(header)  # determine data length
    print(f"[RECEIVING] {data_len} bytes from {addr[0]}:{addr[1]}")
    data = conn.recv(data_len)  # receive data
    obj = pickle.loads(data)  # convert to object

    # Send confirmation
    conn.sendall(CONFIRM_MSG.encode(FORMAT))
    print(f"[RECEIVED] {obj} from {addr[0]}:{addr[1]}")

    # Close the connection
    conn.close()

    received_objects.put(obj)


def broadcast(obj: object):
    # Broadcast an object to all known nodes
    for port in LISTENING_PORTS:
        # spin thread for each sending port and add to queue
        t = Thread(target=send_object, args=(NODE_IP, port, obj))
        t.start()
