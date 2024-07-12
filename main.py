import socket
import time
from collections import defaultdict

import psutil


def get_protocol_name(conn_type):
    if conn_type == socket.SOCK_STREAM:
        return "TCP"
    elif conn_type == socket.SOCK_DGRAM:
        return "UDP"
    elif conn_type == socket.SOCK_RAW:
        return "RAW"
    elif conn_type == socket.SOCK_RDM:
        return "RDM"
    elif conn_type == socket.SOCK_SEQPACKET:
        return "SEQPACKET"
    else:
        return "OTHER"


def calculate_protocol_percentage(protocol_distribution, total_connections):
    protocol_percentage = {}
    for protocol, count in protocol_distribution.items():
        protocol_percentage[protocol] = (
            round((count / total_connections) * 100, 2) if total_connections > 0 else 0
        )
    return protocol_percentage


def get_network_details(interval=60, duration=10):
    total_bytes_received = 0
    total_packets_received = 0
    total_bandwidth = 80 * 1024 * 1024  # 640 Mbps in bytes

    start_time = time.time()
    end_time = start_time + duration * 60

    with open("network_details.txt", "w") as file:
        file.write(
            "Time, TCP (%), UDP (%), Network Utilization (%), Total Bytes Received, Packets Received/sec\n"
        )

        last_bytes_received = 0
        last_packets_received = 0

        while time.time() < end_time:
            # Get network statistics
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()
            bytes_received = net_io.bytes_recv - last_bytes_received
            last_bytes_received = net_io.bytes_recv
            packets_received = net_io.packets_recv - last_packets_received
            last_packets_received = net_io.packets_recv

            # Calculate protocol distribution
            current_protocol_distribution = defaultdict(int)
            for conn in connections:
                protocol_name = get_protocol_name(conn.type)
                current_protocol_distribution[protocol_name] += 1

            total_connections = sum(current_protocol_distribution.values())
            protocol_percentage = calculate_protocol_percentage(
                current_protocol_distribution, total_connections
            )
            tcp_percentage = protocol_percentage.get("TCP", 0)
            udp_percentage = protocol_percentage.get("UDP", 0)

            # Calculate network utilization
            network_utilization = (bytes_received / (total_bandwidth * interval)) * 100

            # Accumulate total bytes and packets
            total_bytes_received += bytes_received
            total_packets_received += packets_received

            print(
                f"{time.strftime('%H:%M:%S')}, {tcp_percentage}, {udp_percentage}, {network_utilization:.2f}, {bytes_received}, {packets_received}\n"
            )

            # Write to file
            file.write(
                f"{time.strftime('%H:%M:%S')}, {tcp_percentage}, {udp_percentage}, {network_utilization:.2f}, {bytes_received}, {packets_received}\n"
            )

            # Sleep for the interval
            time.sleep(interval)


if __name__ == "__main__":
    get_network_details(interval=1, duration=60)
