import socket
import sctp  # Ensure you have an SCTP library (e.g., pysctp)
import threading
import time

# Define edge nodes where traffic will be dispatched (TCP targets)
EDGE_NODES = [
    {"host": "192.168.1.101", "port": 8000, "healthy": True},
    {"host": "192.168.1.102", "port": 8000, "healthy": True},
    {"host": "192.168.1.103", "port": 8000, "healthy": True},
]

HEALTH_CHECK_INTERVAL = 5

# Global variables for round-robin selection
rr_index = 0
rr_lock = threading.Lock()

def check_edge_node(node):
    """Attempt a simple TCP connection to determine health."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((node["host"], node["port"]))
        s.close()
        return True
    except Exception:
        return False

def health_check_thread():
    """Continuously update each edge node’s health status."""
    while True:
        for node in EDGE_NODES:
            node["healthy"] = check_edge_node(node)
            status = "healthy" if node["healthy"] else "unhealthy"
            print(f"Health check: Edge node {node['host']}:{node['port']} is {status}")
        time.sleep(HEALTH_CHECK_INTERVAL)

def select_edge_node():
    """Select a healthy edge node using round-robin."""
    global rr_index
    healthy_nodes = [node for node in EDGE_NODES if node["healthy"]]
    if not healthy_nodes:
        print("No healthy edge nodes available!")
        return None
    with rr_lock:
        node = healthy_nodes[rr_index % len(healthy_nodes)]
        rr_index = (rr_index + 1) % len(healthy_nodes)
    return node

def forward_to_edge(data):
    """Forward the given data to a selected edge node via TCP.
    If the selected node fails during the operation, mark it unhealthy and try another."""
    node = select_edge_node()
    if node is None:
        print("No healthy edge nodes available. Dropping traffic.")
        return None
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((node["host"], node["port"]))
        # Optionally transform or add headers to the data here
        tcp_sock.sendall(data)
        response = tcp_sock.recv(4096)
        tcp_sock.close()
        return response
    except Exception as e:
        print(f"Error forwarding to {node['host']}:{node['port']}: {e}")
        node["healthy"] = False
        return forward_to_edge(data)

def handle_connection(conn, addr):
    """Handle an individual SCTP connection in a separate thread."""
    print(f"Handling connection from {addr}")
    try:
        data = conn.recv(4096)
        print(f"Received SCTP data from {addr}: {data}")
        response = forward_to_edge(data)
        if response:
            conn.send(response)
    except Exception as e:
        print(f"Error handling connection from {addr}: {e}")
    finally:
        conn.close()

def sctp_listener():
    """Listen for SCTP connections and spawn a new thread for each incoming connection."""
    SCTP_HOST = "0.0.0.0"  # Listen on all interfaces
    SCTP_PORT = 9000
    with sctp.sctpsocket_tcp(socket.AF_INET) as server_sock:
        server_sock.bind((SCTP_HOST, SCTP_PORT))
        server_sock.listen(5)
        print(f"SCTP Load Balancer is listening on {SCTP_HOST}:{SCTP_PORT}")
        while True:
            try:
                conn, addr = server_sock.accept()
                print(f"Accepted SCTP connection from {addr}")
                # Spawn a thread to handle this connection concurrently
                threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

if __name__ == "__main__":
    # Start the health-check thread for edge nodes
    threading.Thread(target=health_check_thread, daemon=True).start()
    # Start the SCTP listener which will spawn threads for each connection
    sctp_listener()
