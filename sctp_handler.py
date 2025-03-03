import socket
import sctp 
import threading
import time

# assuming we have three edge nodes
EDGE_NODES = [
    {"host": "192.168.2.210", "port": 8000, "healthy": True},
    {"host": "192.168.2.211", "port": 8000, "healthy": True},
    {"host": "192.168.2.212", "port": 8000, "healthy": True},
]


# Global variables for round-robin selection
rr_index = 0

def check_edge_node(node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node["host"], node["port"]))
    s.close()
    return True
    

def health_check_thread():
    while True:
        for node in EDGE_NODES:
            node["healthy"] = check_edge_node(node)
            status = "healthy" if node["healthy"] else "unhealthy"
        time.sleep(5)

def select_edge_node():
    global rr_index
    healthy_nodes = [node for node in EDGE_NODES if node["healthy"]]
    node = healthy_nodes[rr_index % len(healthy_nodes)]
    rr_index = (rr_index + 1) % len(healthy_nodes)
    return node

def forward_to_edge(data):
    node = select_edge_node()
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((node["host"], node["port"]))
    tcp_sock.sendall(data)
    response = tcp_sock.recv(4096)
    tcp_sock.close()
    return response


def handle_connection(conn, addr):
    
    data = conn.recv(4096)
    response = forward_to_edge(data)
    if response:
        conn.send(response)
    conn.close()

def sctp_listener():
    with sctp.sctpsocket_tcp(socket.AF_INET) as server_sock:
        server_sock.bind(("0.0.0.0", 9000))
        server_sock.listen()
        while True:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()
         

if __name__ == "__main__":
    # Start the health-check thread for edge nodes
    threading.Thread(target=health_check_thread, daemon=True).start()
    # Start the SCTP listener which will spawn threads for each connection
    sctp_listener()
