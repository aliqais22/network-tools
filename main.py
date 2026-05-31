import socket
import subprocess
import urllib.request
from datetime import datetime
import time
import os
import ipaddress

PING_COUNT = "4"
PING_TIMEOUT_MS = "3000"
PORT_TIMEOUT_SECONDS = 3

COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 3306, 3389]


def print_header():
    print("\n============================")
    print(" Network Tools Dashboard")
    print("============================")


def show_menu():
    print("\nChoose an option:")
    print("1) Ping Host")
    print("2) TCP Port Check")
    print("3) DNS Lookup")
    print("4) Local IP")
    print("5) DHCP Information")
    print("6) Public IP Lookup")
    print("7) Traceroute")
    print("8) Multi-Port Scanner")
    print("9) Generate Report")
    print("10) Exit")
    print("11) Full Host Check")
    print("12) Internet Troubleshooter")


def ping_host():
    host = input("Enter host to ping: ").strip()

    if not host:
        print("Please enter a host.")
        return False

    try:
        result = subprocess.run(
            ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            check=False
        )

        output = result.stdout.decode("utf-8", errors="replace")
        error_output = result.stderr.decode("utf-8", errors="replace")

        print(output)

        if error_output:
            print(error_output)

        if result.returncode == 0:
            print(f"SUCCESS: {host} responded.")
            return True
        else:
            print(f"FAILED: {host} did not respond.")
            return False

    except Exception as error:
        print(f"ERROR: {error}")
        return False

def check_tcp_port():
    host = input("Enter host: ").strip()
    port_text = input("Enter TCP port: ").strip()

    if not host:
        print("Please enter a host.")
        return

    try:
        port = int(port_text)
        if port < 1 or port > 65535:
            print("Port must be between 1 and 65535.")
            return
    except ValueError:
        print("Port must be a number.")
        return

    try:
        with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
            print(f"OPEN: TCP port {port} is open on {host}.")
    except socket.timeout:
        print(f"CLOSED/TIMEOUT: TCP port {port} did not respond.")
    except socket.gaierror:
        print(f"ERROR: Could not resolve host: {host}")
    except OSError:
        print(f"CLOSED: TCP port {port} is closed on {host}.")


def dns_lookup():
    domain = input("Enter domain name: ").strip()

    if not domain:
        print("Please enter a domain.")
        return

    try:
        print("\n============================")
        print(" DNS Lookup")
        print("============================")

        ip_address = socket.gethostbyname(domain)

        print(f"Domain: {domain}")
        print(f"Resolved IP: {ip_address}")
        print("DNS Status: SUCCESS")

        print("\n============================")
        print(" Connectivity Test")
        print("============================")

        test_port(domain, 80, "HTTP")
        test_port(domain, 443, "HTTPS")

    except socket.gaierror:
        print(f"DNS FAILED: Could not resolve domain: {domain}")


def test_port(host, port, name=""):
    try:
        with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
            print(f"Port {port} ({name}): OPEN")
            return True
    except OSError:
        print(f"Port {port} ({name}): CLOSED or FILTERED")
        return False


def show_local_ip():
    local_ip = get_local_ip()
    print(f"Your local IP address is: {local_ip}")


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
            test_socket.connect(("8.8.8.8", 80))
            return test_socket.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "Unknown"


def dhcp_information():
    print("\n============================")
    print(" DHCP Information")
    print("============================")

    try:
        result = subprocess.run(
            ["ipconfig", "/all"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            check=False
        )

        output = result.stdout.decode("utf-8", errors="ignore")

        if not output:
            print("ERROR: Could not read DHCP information.")
            return

        keywords = [
            "DHCP Enabled",
            "IPv4 Address",
            "Subnet Mask",
            "Default Gateway",
            "DNS Servers"
        ]

        found = False

        for line in output.splitlines():
            for keyword in keywords:
                if keyword in line:
                    print(line.strip())
                    found = True

        if "DHCP Enabled" in output:
            print("\nDHCP Status: DHCP information found.")
        else:
            print("\nDHCP Status: Could not detect DHCP information.")

        if not found:
            print("No DHCP details found. Your Windows language may be different.")

    except Exception as error:
        print(f"ERROR: Could not read DHCP information. Details: {error}")
def public_ip_lookup():
    print("\n============================")
    print(" Public IP Lookup")
    print("============================")

    local_ip = get_local_ip()
    print(f"Local IP: {local_ip}")

    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            public_ip = response.read().decode("utf-8")
            print(f"Public IP: {public_ip}")
    except Exception as error:
        print(f"ERROR: Could not get public IP. Details: {error}")


def traceroute():
    def traceroute():
        host = input("Enter host for traceroute: ").strip()

        if not host:
            print("Please enter a host.")
            return

        print(f"\nRunning traceroute to {host}...\n")

        try:
            result = subprocess.run(
                ["tracert", host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                check=False
            )

            output = result.stdout.decode("utf-8", errors="replace")
            error_output = result.stderr.decode("utf-8", errors="replace")

            print(output)

            if error_output:
                print(error_output)

        except FileNotFoundError:
            print("ERROR: tracert command not found.")
        except Exception as error:
            print(f"ERROR: Could not run traceroute. Details: {error}")


def multi_port_scanner():
    host = input("Enter host to scan: ").strip()

    if not host:
        print("Please enter a host.")
        return

    print(f"\nScanning common ports on {host}...\n")

    start_time = time.time()

    for port in COMMON_PORTS:
        try:
            with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
                print(f"Port {port}: OPEN")
        except socket.gaierror:
            print(f"ERROR: Could not resolve host: {host}")
            return
        except OSError:
            print(f"Port {port}: CLOSED or FILTERED")

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nScan completed in {duration:.2f} seconds.")

def full_host_check():
    host = input("Enter host for full check: ").strip()

    if not host:
        print("Please enter a host.")
        return

    print("\n============================")
    print(" Full Host Check")
    print("============================")
    print(f"Target Host: {host}")

    score = 0
    max_score = 100

    # DNS CHECK
    print("\n[1] DNS Lookup")
    try:
        ip_address = socket.gethostbyname(host)
        print(f"DNS Status: SUCCESS")
        print(f"Resolved IP: {ip_address}")
        score += 20
    except socket.gaierror:
        print("DNS Status: FAILED")
        print("Could not resolve host.")
        print("\nFinal Result: Host check stopped because DNS failed.")
        return

    # PING CHECK
    print("\n[2] Ping Test")
    try:
        result = subprocess.run(
            ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print("Ping Status: SUCCESS")
            score += 20
        else:
            print("Ping Status: FAILED or BLOCKED")

    except Exception as error:
        print(f"Ping Error: {error}")

    # HTTP / HTTPS CHECK
    print("\n[3] Web Ports Check")

    if test_port(host, 80, "HTTP"):
        score += 15

    if test_port(host, 443, "HTTPS"):
        score += 15

    # COMMON PORTS CHECK
    print("\n[4] Common Ports Scan")

    open_ports = []

    for port in COMMON_PORTS:
        try:
            with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
                print(f"Port {port}: OPEN")
                open_ports.append(port)
        except OSError:
            print(f"Port {port}: CLOSED or FILTERED")

    if open_ports:
        score += 10

    # TRACEROUTE
    print("\n[5] Traceroute")
    try:
        result = subprocess.run(
            ["tracert", host],
            capture_output=True,
            text=True,
            check=False
        )

        print(result.stdout)
        score += 20

    except Exception as error:
        print(f"Traceroute Error: {error}")

    # SUMMARY
    print("\n============================")
    print(" Diagnosis Summary")
    print("============================")

    print(f"Target Host: {host}")
    print(f"Resolved IP: {ip_address}")
    print(f"Open Ports: {open_ports if open_ports else 'None detected'}")
    print(f"Network Health Score: {score}/{max_score}")

    if score >= 80:
        print("Status: Excellent - Host looks reachable and healthy.")
    elif score >= 50:
        print("Status: Medium - Host is reachable but some checks failed.")
    else:
        print("Status: Weak - Host has connection or filtering issues.")

def generate_report():
    print("\nGenerating network report...")

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/network_report_{timestamp}.txt"

    local_ip = get_local_ip()

    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            public_ip = response.read().decode("utf-8")
    except Exception:
        public_ip = "Could not detect"

    report_content = f"""
Network Tools Dashboard Report
Generated at: {datetime.now()}

Local IP: {local_ip}
Public IP: {public_ip}

Included Tools:
- Ping Host
- TCP Port Check
- DNS Lookup
- DHCP Information
- Public IP Lookup
- Traceroute
- Multi-Port Scanner

Notes:
This report was generated by a beginner-friendly Python networking toolkit.
"""

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report_content)

        print(f"Report saved to: {filename}")

    except Exception as error:
        print(f"ERROR: Could not save report. Details: {error}")


def ping_target(host):
    try:
        result = subprocess.run(
            ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False


def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def is_apipa_address(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip in ipaddress.ip_network("169.254.0.0/16")
    except ValueError:
        return False


def get_public_ip_safely():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None


def internet_troubleshooter():
    print("\n============================")
    print(" Internet Troubleshooter")
    print("============================")

    print("\nThis tool will check your internet connection and suggest possible fixes.\n")

    local_ip = get_local_ip()
    public_ip = get_public_ip_safely()

    print(f"Local IP: {local_ip}")
    print(f"Public IP: {public_ip if public_ip else 'Could not detect'}")

    problems = []
    solutions = []
    score = 0

    # 1. Local IP check
    print("\n[1] Checking Local IP...")

    if local_ip == "Unknown":
        print("Status: FAILED")
        problems.append("Your device does not have a valid local IP address.")
        solutions.append("Make sure Wi-Fi or Ethernet is connected.")
        solutions.append("Disable and enable the network adapter.")
        solutions.append("Restart your computer and router.")
    elif is_apipa_address(local_ip):
        print("Status: DHCP PROBLEM")
        problems.append("Your device received a 169.254.x.x address. This usually means DHCP failed.")
        solutions.append("Restart the router.")
        solutions.append("Reconnect to the Wi-Fi network.")
        solutions.append("Run: ipconfig /release")
        solutions.append("Then run: ipconfig /renew")
    else:
        print("Status: OK")
        score += 20

    # 2. Internet IP ping check
    print("\n[2] Checking connection to the internet using 8.8.8.8...")

    internet_ping = ping_target("8.8.8.8")

    if internet_ping:
        print("Status: OK - Internet IP is reachable.")
        score += 25
    else:
        print("Status: FAILED - Could not reach internet IP.")
        problems.append("Your device may be connected to the router, but the router may not have internet.")
        solutions.append("Restart the router.")
        solutions.append("Check if the internet cable is connected.")
        solutions.append("Check if there is an outage from the internet provider.")
        solutions.append("Contact your ISP if the problem continues.")

    # 3. DNS check
    print("\n[3] Checking DNS resolution...")

    try:
        google_ip = socket.gethostbyname("google.com")
        print(f"Status: OK - google.com resolved to {google_ip}")
        dns_ok = True
        score += 25
    except socket.gaierror:
        print("Status: FAILED - DNS is not working.")
        dns_ok = False
        problems.append("DNS is not working. The internet may work, but domain names are not resolving.")
        solutions.append("Run: ipconfig /flushdns")
        solutions.append("Change DNS to 8.8.8.8 or 1.1.1.1")
        solutions.append("Restart the router.")

    # 4. Website HTTPS check
    print("\n[4] Checking website access using HTTPS...")

    if dns_ok and is_port_open("google.com", 443):
        print("Status: OK - HTTPS websites are reachable.")
        score += 20
    else:
        print("Status: FAILED or BLOCKED - HTTPS test failed.")
        problems.append("Secure websites may be blocked or unreachable.")
        solutions.append("Check firewall or antivirus settings.")
        solutions.append("Try another browser.")
        solutions.append("Restart the router.")

    # 5. Public IP check
    print("\n[5] Checking Public IP...")

    if public_ip:
        print("Status: OK - Public IP detected.")
        score += 10
    else:
        print("Status: WARNING - Could not detect public IP.")
        problems.append("The computer could not detect a public IP.")
        solutions.append("Check internet connection.")
        solutions.append("Try again later.")
        solutions.append("Check if a firewall is blocking the request.")

    # Summary
    print("\n============================")
    print(" Troubleshooting Summary")
    print("============================")

    print(f"Internet Health Score: {score}/100")

    if score >= 80:
        print("Overall Status: GOOD")
        print("Your internet connection looks healthy.")
    elif score >= 50:
        print("Overall Status: MEDIUM")
        print("Some parts of your connection work, but there may be a problem.")
    else:
        print("Overall Status: WEAK")
        print("There is likely a network or internet problem.")

    print("\nDetected Problems:")

    if problems:
        for index, problem in enumerate(problems, start=1):
            print(f"{index}) {problem}")
    else:
        print("No major problems detected.")

    print("\nSuggested Solutions:")

    if solutions:
        unique_solutions = list(dict.fromkeys(solutions))
        for index, solution in enumerate(unique_solutions, start=1):
            print(f"{index}) {solution}")
    else:
        print("No action needed.")

    print("\nImportant: This tool gives suggestions, but some problems may require checking the router or contacting the internet provider.")

def main():
    while True:
        print_header()
        show_menu()

        choice = input("\nEnter your choice (1-12): ").strip()

        if choice == "1":
            ping_host()
        elif choice == "2":
            check_tcp_port()
        elif choice == "3":
            dns_lookup()
        elif choice == "4":
            show_local_ip()
        elif choice == "5":
            dhcp_information()
        elif choice == "6":
            public_ip_lookup()
        elif choice == "7":
            traceroute()
        elif choice == "8":
            multi_port_scanner()
        elif choice == "9":
            generate_report()
        elif choice == "10":
            print("Goodbye!")
        elif choice == "11":
            full_host_check()
        elif choice == "12":
            internet_troubleshooter()
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 12.")

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
