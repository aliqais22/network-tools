import socket
import subprocess
import urllib.error
import urllib.request
import re


PING_COUNT = "4"
PING_TIMEOUT_MS = "3000"
TCP_TIMEOUT_SECONDS = 3
DEFAULT_SCAN_PORTS = "21,22,25,53,80,110,143,443,587,993,995,3389"


def run_command(command, timeout=None):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return result, None
    except FileNotFoundError as error:
        return None, error
    except subprocess.TimeoutExpired as error:
        return error, error


def check_tcp_port(host, port, timeout=TCP_TIMEOUT_SECONDS):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return f"OPEN: TCP port {port} is open on {host}."
    except socket.timeout:
        return f"CLOSED/TIMED OUT: TCP port {port} did not respond within {timeout} seconds."
    except socket.gaierror:
        return f"ERROR: Could not resolve host name: {host}"
    except OSError:
        return f"CLOSED: TCP port {port} is not open on {host}."


def resolve_host_addresses(host):
    try:
        addresses = socket.getaddrinfo(host, None)
        return sorted({item[4][0] for item in addresses}), None
    except socket.gaierror as error:
        return [], error


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
            test_socket.connect(("8.8.8.8", 80))
            return test_socket.getsockname()[0], None
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname()), None
        except socket.gaierror as error:
            return None, error


def get_public_ip(timeout=8):
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=timeout) as response:
            return response.read().decode("utf-8").strip(), None
    except (urllib.error.URLError, TimeoutError) as error:
        return None, error


def parse_ports(text):
    ports = set()
    parts = [part.strip() for part in text.split(",") if part.strip()]

    for part in parts:
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            try:
                start_port = int(start_text.strip())
                end_port = int(end_text.strip())
            except ValueError:
                return []
            if start_port > end_port:
                start_port, end_port = end_port, start_port
            for port in range(start_port, end_port + 1):
                if 1 <= port <= 65535:
                    ports.add(port)
        else:
            try:
                port = int(part)
            except ValueError:
                return []
            if 1 <= port <= 65535:
                ports.add(port)

    return sorted(ports)


def parse_ping_quality_output(output, expected_packets):
    packet_match = re.search(
        r"Sent\s*=\s*(\d+).*?Received\s*=\s*(\d+).*?Lost\s*=\s*(\d+)",
        output,
        re.IGNORECASE | re.DOTALL,
    )
    loss_match = re.search(r"\((\d+)%\s*loss\)", output, re.IGNORECASE)
    latency_match = re.search(
        r"Minimum\s*=\s*(\d+)ms,\s*Maximum\s*=\s*(\d+)ms,\s*Average\s*=\s*(\d+)ms",
        output,
        re.IGNORECASE,
    )
    reply_times = [int(value) for value in re.findall(r"time[=<]\s*(\d+)\s*ms", output, re.IGNORECASE)]

    if packet_match:
        packets_sent = int(packet_match.group(1))
        packets_received = int(packet_match.group(2))
        packets_lost = int(packet_match.group(3))
    else:
        packets_sent = expected_packets
        packets_received = len(reply_times)
        packets_lost = max(packets_sent - packets_received, 0)

    if loss_match:
        packet_loss_percent = int(loss_match.group(1))
    elif packets_sent:
        packet_loss_percent = (packets_lost / packets_sent) * 100
    else:
        packet_loss_percent = 100

    if latency_match:
        min_ping = int(latency_match.group(1))
        max_ping = int(latency_match.group(2))
        avg_ping = int(latency_match.group(3))
    elif reply_times:
        min_ping = min(reply_times)
        max_ping = max(reply_times)
        avg_ping = sum(reply_times) / len(reply_times)
    else:
        min_ping = None
        max_ping = None
        avg_ping = None

    if len(reply_times) >= 2:
        differences = [abs(reply_times[index] - reply_times[index - 1]) for index in range(1, len(reply_times))]
        jitter = sum(differences) / len(differences)
    else:
        jitter = None

    return {
        "packets_sent": packets_sent,
        "packets_received": packets_received,
        "packets_lost": packets_lost,
        "packet_loss_percent": packet_loss_percent,
        "min_ping": min_ping,
        "max_ping": max_ping,
        "avg_ping": avg_ping,
        "jitter": jitter,
    }


def format_ms_value(value):
    if value is None:
        return "Not available"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.1f} ms"
    return f"{value:.0f} ms"
