import os
import socket
import subprocess
import threading
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from tkinter import END, filedialog, messagebox, scrolledtext, ttk
import tkinter as tk


PING_COUNT = "4"
PING_TIMEOUT_MS = "3000"
TCP_TIMEOUT_SECONDS = 3
DEFAULT_SCAN_PORTS = "21,22,25,53,80,110,143,443,587,993,995,3389"


class SmartInternetTroubleshooter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Internet Troubleshooter")
        self.geometry("980x720")
        self.minsize(860, 600)

        self.host_var = tk.StringVar(value="google.com")
        self.port_var = tk.StringVar(value="80")
        self.scan_ports_var = tk.StringVar(value=DEFAULT_SCAN_PORTS)
        self.status_var = tk.StringVar(value="Ready")
        self.logs_folder = Path(__file__).resolve().parent / "logs"
        self.logs_folder.mkdir(exist_ok=True)

        self._build_window()

    def _build_window(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            root,
            text="Smart Internet Troubleshooter",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            root,
            text="Simple Windows network checks for hosts, ports, DNS, IP addresses, DHCP, and routes.",
        )
        subtitle.pack(anchor=tk.W, pady=(2, 12))

        inputs = ttk.LabelFrame(root, text="Inputs", padding=10)
        inputs.pack(fill=tk.X, pady=(0, 10))
        inputs.columnconfigure(1, weight=1)
        inputs.columnconfigure(3, weight=1)

        ttk.Label(inputs, text="Host / Domain").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        ttk.Entry(inputs, textvariable=self.host_var).grid(row=0, column=1, sticky=tk.EW, padx=(0, 12))

        ttk.Label(inputs, text="Port").grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        ttk.Entry(inputs, textvariable=self.port_var, width=12).grid(row=0, column=3, sticky=tk.W)

        ttk.Label(inputs, text="Multi-Port List").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        ttk.Entry(inputs, textvariable=self.scan_ports_var).grid(
            row=1,
            column=1,
            columnspan=3,
            sticky=tk.EW,
            pady=(8, 0),
        )

        buttons = ttk.LabelFrame(root, text="Tools", padding=10)
        buttons.pack(fill=tk.X, pady=(0, 10))

        button_specs = [
            ("Ping Host", self.ping_host),
            ("TCP Port Check", self.tcp_port_check),
            ("DNS Lookup", self.dns_lookup),
            ("Local IP", self.local_ip),
            ("DHCP Information", self.dhcp_information),
            ("Public IP Lookup", self.public_ip_lookup),
            ("Traceroute", self.traceroute),
            ("Multi-Port Scanner", self.multi_port_scanner),
            ("Full Host Check", self.full_host_check),
            ("Internet Troubleshooter", self.internet_troubleshooter),
        ]

        for index, (text, command) in enumerate(button_specs):
            button = ttk.Button(buttons, text=text, command=command)
            button.grid(row=index // 5, column=index % 5, sticky=tk.EW, padx=4, pady=4)
            buttons.columnconfigure(index % 5, weight=1)

        actions = ttk.Frame(root)
        actions.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(actions, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT)
        ttk.Button(actions, text="Save Report", command=self.save_report).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Open Logs Folder", command=self.open_logs_folder).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(actions, textvariable=self.status_var).pack(side=tk.RIGHT)

        output_frame = ttk.LabelFrame(root, text="Results", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True)

        self.write_line("Welcome. Enter a host/domain and choose a tool to begin.")

    def run_in_background(self, title, task):
        self.status_var.set(f"Running: {title}")
        self.write_section(title)

        def worker():
            try:
                task()
            except Exception as error:
                self.write_line(f"ERROR: {error}")
            finally:
                self.status_var.set("Ready")

        threading.Thread(target=worker, daemon=True).start()

    def write_section(self, title):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_line("")
        self.write_line("=" * 72)
        self.write_line(f"{title} - {timestamp}")
        self.write_line("=" * 72)

    def write_line(self, text=""):
        self.log_line(text)
        self.output.after(0, self._append_text, f"{text}\n")

    def _append_text(self, text):
        self.output.insert(END, text)
        self.output.see(END)

    def log_line(self, text=""):
        log_file = self.logs_folder / f"network_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = str(text).splitlines() or [""]

        with log_file.open("a", encoding="utf-8") as file:
            for line in lines:
                file.write(f"[{timestamp}] {line}\n")

    def clear_output(self):
        self.output.delete("1.0", END)
        self.status_var.set("Output cleared")

    def save_report(self):
        report = self.output.get("1.0", END).strip()
        if not report:
            messagebox.showinfo("Save Report", "There is no output to save yet.")
            return

        default_name = f"internet_troubleshooter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            Path(file_path).write_text(report, encoding="utf-8")
            self.status_var.set(f"Saved report: {file_path}")
            messagebox.showinfo("Save Report", "Report saved successfully.")

    def open_logs_folder(self):
        self.logs_folder.mkdir(exist_ok=True)
        try:
            os.startfile(str(self.logs_folder))
        except OSError as error:
            messagebox.showerror("Open Logs Folder", f"Could not open logs folder.\n\n{error}")

    def get_host(self):
        host = self.host_var.get().strip()
        if not host:
            self.write_line("Please enter a host name or IP address.")
            return None
        return host

    def get_port(self):
        port_text = self.port_var.get().strip()
        try:
            port = int(port_text)
        except ValueError:
            self.write_line("Please enter a valid port number.")
            return None

        if port < 1 or port > 65535:
            self.write_line("Please enter a port number from 1 to 65535.")
            return None

        return port

    def run_command(self, command, error_message):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError:
            self.write_line(error_message)
            return None

        if result.stdout:
            self.write_line(result.stdout.rstrip())
        if result.stderr:
            self.write_line(result.stderr.rstrip())

        return result

    def ping_host(self):
        host = self.get_host()
        if not host:
            return

        def task():
            self.write_line(f"Pinging {host}...")
            result = self.run_command(
                ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
                "ERROR: The Windows ping command was not found.",
            )
            if result is None:
                return
            if result.returncode == 0:
                self.write_line(f"SUCCESS: {host} responded to ping.")
            else:
                self.write_line(f"FAILED: {host} did not respond to ping.")

        self.run_in_background("Ping Host", task)

    def tcp_port_check(self):
        host = self.get_host()
        port = self.get_port()
        if not host or port is None:
            return

        def task():
            self.write_line(f"Checking TCP connection to {host}:{port}...")
            self.write_line(self.check_port(host, port))

        self.run_in_background("TCP Port Check", task)

    def dns_lookup(self):
        host = self.get_host()
        if not host:
            return

        def task():
            try:
                self.write_line(f"Resolving {host}...")
                addresses = socket.getaddrinfo(host, None)
                unique_ips = sorted({item[4][0] for item in addresses})
                for ip_address in unique_ips:
                    self.write_line(f"{host} resolves to {ip_address}")
            except socket.gaierror:
                self.write_line(f"ERROR: Could not resolve host name: {host}")

        self.run_in_background("DNS Lookup", task)

    def local_ip(self):
        def task():
            self.write_line(f"Computer name: {socket.gethostname()}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
                    test_socket.connect(("8.8.8.8", 80))
                    local_ip = test_socket.getsockname()[0]
                self.write_line(f"Local IP address: {local_ip}")
            except OSError:
                try:
                    self.write_line(f"Local IP address: {socket.gethostbyname(socket.gethostname())}")
                except socket.gaierror:
                    self.write_line("ERROR: Could not find the local IP address.")

        self.run_in_background("Local IP", task)

    def dhcp_information(self):
        def task():
            self.write_line("Showing Windows IP configuration and DHCP details...")
            self.run_command(
                ["ipconfig", "/all"],
                "ERROR: The Windows ipconfig command was not found.",
            )

        self.run_in_background("DHCP Information", task)

    def public_ip_lookup(self):
        def task():
            self.write_line("Looking up public IP address...")
            try:
                with urllib.request.urlopen("https://api.ipify.org", timeout=8) as response:
                    public_ip = response.read().decode("utf-8").strip()
                self.write_line(f"Public IP address: {public_ip}")
            except (urllib.error.URLError, TimeoutError) as error:
                self.write_line(f"ERROR: Could not look up public IP address. Details: {error}")

        self.run_in_background("Public IP Lookup", task)

    def traceroute(self):
        host = self.get_host()
        if not host:
            return

        def task():
            self.write_line(f"Tracing route to {host}...")
            self.run_command(
                ["tracert", host],
                "ERROR: The Windows tracert command was not found.",
            )

        self.run_in_background("Traceroute", task)

    def multi_port_scanner(self):
        host = self.get_host()
        if not host:
            return

        ports = self.parse_ports(self.scan_ports_var.get())
        if not ports:
            self.write_line("Please enter ports like 80,443,3389 or ranges like 20-25.")
            return

        def task():
            self.write_line(f"Scanning {len(ports)} TCP port(s) on {host}...")
            for port in ports:
                self.write_line(self.check_port(host, port))

        self.run_in_background("Multi-Port Scanner", task)

    def full_host_check(self):
        host = self.get_host()
        if not host:
            return

        def task():
            self.write_line(f"Running a full check for {host}.")
            self.write_line("")
            self.write_line("[DNS]")
            try:
                ip_address = socket.gethostbyname(host)
                self.write_line(f"{host} resolves to {ip_address}")
            except socket.gaierror:
                self.write_line(f"ERROR: Could not resolve host name: {host}")

            self.write_line("")
            self.write_line("[Ping]")
            ping_result = self.run_command(
                ["ping", "-n", PING_COUNT, "-w", PING_TIMEOUT_MS, host],
                "ERROR: The Windows ping command was not found.",
            )
            if ping_result is not None and ping_result.returncode == 0:
                self.write_line("Ping result: SUCCESS")
            elif ping_result is not None:
                self.write_line("Ping result: FAILED")

            self.write_line("")
            self.write_line("[Common TCP Ports]")
            for port in [80, 443, 53, 22, 3389]:
                self.write_line(self.check_port(host, port))

        self.run_in_background("Full Host Check", task)

    def internet_troubleshooter(self):
        def task():
            self.write_line("Running basic internet troubleshooting checks.")

            self.write_line("")
            self.write_line("[Local IP]")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
                    test_socket.connect(("8.8.8.8", 80))
                    self.write_line(f"Local IP address: {test_socket.getsockname()[0]}")
            except OSError:
                self.write_line("Could not confirm local IP using an outbound test socket.")

            self.write_line("")
            self.write_line("[Default Windows Network Details]")
            self.run_command(
                ["ipconfig"],
                "ERROR: The Windows ipconfig command was not found.",
            )

            self.write_line("")
            self.write_line("[DNS Test]")
            try:
                self.write_line(f"google.com resolves to {socket.gethostbyname('google.com')}")
            except socket.gaierror:
                self.write_line("DNS test failed: could not resolve google.com.")

            self.write_line("")
            self.write_line("[Internet Ping Test]")
            self.run_command(
                ["ping", "-n", "4", "-w", PING_TIMEOUT_MS, "8.8.8.8"],
                "ERROR: The Windows ping command was not found.",
            )

            self.write_line("")
            self.write_line("[Public IP]")
            try:
                with urllib.request.urlopen("https://api.ipify.org", timeout=8) as response:
                    self.write_line(f"Public IP address: {response.read().decode('utf-8').strip()}")
            except (urllib.error.URLError, TimeoutError) as error:
                self.write_line(f"Public IP lookup failed: {error}")

            self.write_line("")
            self.write_line("Troubleshooter finished.")

        self.run_in_background("Internet Troubleshooter", task)

    def check_port(self, host, port):
        try:
            with socket.create_connection((host, port), timeout=TCP_TIMEOUT_SECONDS):
                return f"OPEN: TCP port {port} is open on {host}."
        except socket.timeout:
            return f"CLOSED/TIMED OUT: TCP port {port} did not respond within {TCP_TIMEOUT_SECONDS} seconds."
        except socket.gaierror:
            return f"ERROR: Could not resolve host name: {host}"
        except OSError:
            return f"CLOSED: TCP port {port} is not open on {host}."

    def parse_ports(self, text):
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


if __name__ == "__main__":
    app = SmartInternetTroubleshooter()
    app.mainloop()
