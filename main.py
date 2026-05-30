import socket
import subprocess


PING_COUNT = "4"
PING_TIMEOUT_MS = "3000"
PORT_TIMEOUT_SECONDS = 3


def print_header():
    """Print the dashboard title."""
    print("\n============================")
    print(" Network Tools Dashboard")
    print("============================")


def show_menu():
    """Display the main menu options."""
    print("\nChoose an option:")
    print("1) Ping a host")
    print("2) Check if a TCP port is open")
    print("3) DNS lookup")
    print("4) Show my local IP address")
    print("5) Exit")


def ping_host():
    """Ask for a host and run the Windows ping command."""
    host = input("Enter a host to ping (example: google.com): ").strip()

    if not host:
        print("Please enter a host name or IP address.")
        return

    print(f"\nPinging {host}...\n")

    try:
        # Windows ping options:
        # -n sets the number of echo requests.
        # -w sets the timeout for each reply in milliseconds.
        result = subprocess.run(
            ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
            capture_output=True,
            text=True,
            check=False,
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"SUCCESS: {host} responded to ping.")
        else:
            print(f"FAILED: {host} did not respond to ping.")

    except FileNotFoundError:
        print("ERROR: The ping command was not found on this computer.")
    except Exception as error:
        print(f"ERROR: Could not run ping. Details: {error}")


def check_tcp_port():
    """Ask for a host and port, then check whether the TCP port is open."""
    host = input("Enter a host (example: example.com): ").strip()
    port_text = input("Enter a TCP port (example: 80): ").strip()

    if not host:
        print("Please enter a host name or IP address.")
        return

    try:
        port = int(port_text)
        if port < 1 or port > 65535:
            print("Please enter a port number from 1 to 65535.")
            return
    except ValueError:
        print("Please enter a valid number for the port.")
        return

    print(f"\nChecking {host}:{port}...")

    try:
        # create_connection tries to open a TCP connection.
        # If it succeeds, the port is open from this computer.
        with socket.create_connection((host, port), timeout=PORT_TIMEOUT_SECONDS):
            print(f"OPEN: TCP port {port} is open on {host}.")
    except socket.timeout:
        print(f"CLOSED/TIMED OUT: TCP port {port} did not respond within 3 seconds.")
    except socket.gaierror:
        print(f"ERROR: Could not resolve host name: {host}")
    except OSError:
        print(f"CLOSED: TCP port {port} is not open on {host}.")


def dns_lookup():
    """Resolve a domain name to an IP address."""
    domain = input("Enter a domain name (example: python.org): ").strip()

    if not domain:
        print("Please enter a domain name.")
        return

    try:
        ip_address = socket.gethostbyname(domain)
        print(f"{domain} resolves to {ip_address}")
    except socket.gaierror:
        print(f"ERROR: Could not resolve domain name: {domain}")


def show_local_ip():
    """Show the local IP address of this computer."""
    try:
        # This does not send data to the internet. It asks the OS which local
        # address would be used for an outbound connection.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
            test_socket.connect(("8.8.8.8", 80))
            local_ip = test_socket.getsockname()[0]

        print(f"Your local IP address is: {local_ip}")
    except OSError:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            print(f"Your local IP address is: {local_ip}")
        except socket.gaierror:
            print("ERROR: Could not find the local IP address.")


def main():
    """Run the Network Tools Dashboard."""
    while True:
        print_header()
        show_menu()

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            ping_host()
        elif choice == "2":
            check_tcp_port()
        elif choice == "3":
            dns_lookup()
        elif choice == "4":
            show_local_ip()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
