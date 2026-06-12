import ipaddress
import re
import socket
import subprocess


def extract_ipv4_from_text(text):
    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    if not match:
        return None

    ip_text = match.group(0)
    try:
        return str(ipaddress.IPv4Address(ip_text))
    except ipaddress.AddressValueError:
        return None


def is_supported_private_lan_ip(ip_address):
    ip = ipaddress.IPv4Address(ip_address)
    supported_networks = (
        ipaddress.IPv4Network("10.0.0.0/8"),
        ipaddress.IPv4Network("172.16.0.0/12"),
        ipaddress.IPv4Network("192.168.0.0/16"),
    )
    return any(ip in network for network in supported_networks)


def get_active_network_details():
    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return None

    adapters = []
    current_adapter = None
    waiting_for_gateway_value = False

    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.lower().endswith(":") and "adapter" in stripped.lower():
            current_adapter = {"name": stripped[:-1], "ip": None, "subnet_mask": None, "gateway": None}
            adapters.append(current_adapter)
            waiting_for_gateway_value = False
            continue

        if current_adapter is None:
            continue

        if waiting_for_gateway_value:
            gateway_ip = extract_ipv4_from_text(stripped)
            if gateway_ip:
                current_adapter["gateway"] = gateway_ip
                waiting_for_gateway_value = False
                continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.lower()
        value = value.strip()

        if "ipv4 address" in key:
            current_adapter["ip"] = extract_ipv4_from_text(value)
        elif "subnet mask" in key:
            current_adapter["subnet_mask"] = extract_ipv4_from_text(value)
        elif "default gateway" in key:
            gateway_ip = extract_ipv4_from_text(value)
            if gateway_ip:
                current_adapter["gateway"] = gateway_ip
                waiting_for_gateway_value = False
            else:
                waiting_for_gateway_value = True

    for adapter in adapters:
        local_ip = adapter["ip"]
        subnet_mask = adapter["subnet_mask"]
        gateway = adapter["gateway"]
        if not local_ip or not subnet_mask or not gateway:
            continue
        if is_supported_private_lan_ip(local_ip):
            return adapter

    return None


def calculate_scan_plan(adapter, max_hosts=1024):
    local_ip = adapter["ip"]
    subnet_mask = adapter["subnet_mask"]
    gateway = adapter["gateway"]

    try:
        network = ipaddress.IPv4Network((local_ip, subnet_mask), strict=False)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return None, [], "Could not detect local IP/subnet mask for discovery."

    usable_host_count = max(network.num_addresses - 2, 0)
    if usable_host_count > max_hosts:
        return network, [], "Subnet is too large to scan safely. Please use a smaller subnet or manual range."

    scan_addresses = [str(address) for address in network.hosts()]
    if not scan_addresses:
        return network, [], "No usable host addresses were found in this subnet."

    return network, scan_addresses, None


def get_known_device_addresses(devices):
    known_addresses = set()
    for device in devices:
        address = device["address"].strip()
        if not address:
            continue

        known_addresses.add(address.lower())
        try:
            known_addresses.add(socket.gethostbyname(address))
        except socket.gaierror:
            pass

    return known_addresses


def ping_discovery_address(address):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "300", address],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=2,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_mac_address(address):
    try:
        result = subprocess.run(
            ["arp", "-a", address],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "MAC unavailable"

    match = re.search(r"([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}", result.stdout)
    if match:
        return match.group(0)
    return "MAC not found"


def discover_single_address(address, known_addresses, cancel_event):
    if cancel_event.is_set():
        return None
    if not ping_discovery_address(address):
        return None
    if cancel_event.is_set():
        return None

    mac_address = get_mac_address(address)
    status = "KNOWN" if address.lower() in known_addresses else "UNKNOWN"
    return address, mac_address, status
