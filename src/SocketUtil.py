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
NODE_IP = socket.gethostbyname(socket.gethostname())
HEADER_LEN = 64
FORMAT = 'utf-8'
SEND_TIMEOUT = 30
MAX_CONNECTIONS = 5
NODE_PORT = 5050

# TODO: change print statements to logging statements

# HARDCODED NODES FOR TESTING
NODES = {"goodchain_node_1", "goodchain_node_2",
         "goodchain_node_3", "goodchain_node_4"}

# NODES = socket.request("https://www.goodchain.com/nodes").json()

CONFIRM_MSG = "Object received"
CONFIRM_MSG_LEN = len(CONFIRM_MSG.encode(FORMAT))

received_objects = Queue()


def start_listening_thread():
    # Spin a secondary thread for listening
    # Daemon so it will close when the main window is closed.
    t = Thread(target=start_listening, daemon=True)
    t.start()


def start_listening():
    # Create the socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the IP and port
        s.bind((NODE_IP, NODE_PORT))

        # Listen for incoming connections
        s.listen(MAX_CONNECTIONS)

        print(f"[LISTENING] Node is listening on {NODE_IP}:{NODE_PORT}")

        while True:
            # Wait for the connection
            conn, addr = s.accept()
            print(f"[NEW CONNECTION] {addr[0]}:{addr[1]} connected.")

            # Spin a tertiary thread once there is a connection
            t = Thread(target=receive_object, args=(conn, addr))
            t.start()

    except OSError as e:
        print(e)
    finally:
        s.close()


def send_object(recv_ip: str, recv_port: int, obj: object):
    # Create the socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.settimeout(SEND_TIMEOUT)

    try:  # Connect to the node
        s.connect((recv_ip, recv_port))

        # prepare the object and header
        data = pickle.dumps(obj)
        data_size = len(data)
        header = str(data_size).encode(FORMAT)
        header += b' ' * (HEADER_LEN - len(header))

        print(f"[SENDING] {data_size} bytes to {recv_ip}:{recv_port}")
        s.sendall(header)  # send header
        s.sendall(data)  # send data

        # receive confirmation
        print(f"{recv_ip}:{recv_port} says: {s.recv(CONFIRM_MSG_LEN).decode(FORMAT)}")

    except OSError as e:
        print(e)
    finally:
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
    for node in NODES:
        # spin thread for each sending port and add to queue
        # Not a daemon so all transmissions complete before main thread exits in case the application is closed when sending.
        node_ip = socket.gethostbyname(node)
        if NODE_IP != node_ip:
            # Don't send to self
            t = Thread(target=send_object, args=(
                node_ip, NODE_PORT, obj), daemon=False)
            t.start()
