# Smart Internet Troubleshooter

A lightweight IT network monitoring and troubleshooting dashboard for Windows, built with Python and Tkinter.

Smart Internet Troubleshooter gives small companies and IT technicians a single desktop app to diagnose internet problems, check company devices, discover hosts on the local network, and measure connection quality — with automatic daily logging of every action.

## Current Status

**Version 0.6 — Modern Dashboard UI.** The app is fully functional and refactored into clean modules, with a business-style dashboard interface (sidebar navigation, status cards, live health summaries, and a persistent results console). It runs as a plain Python script; no installation beyond Python itself is required.

## Features

### Basic Network Tools
- **Ping Host** — reachability test with success/failure summary
- **TCP Port Check** — test a single TCP port on any host
- **DNS Lookup** — resolve a hostname to all of its IP addresses
- **Local IP** — show computer name and local IP address
- **DHCP Information** — full Windows IP configuration (`ipconfig /all`)
- **Public IP Lookup** — discover your current public IP address
- **Traceroute** — trace the route to any host
- **Multi-Port Scanner** — scan a list or range of TCP ports (e.g. `80,443` or `20-25`)
- **Full Host Check** — combined DNS + ping + common-ports check for one host
- **Internet Troubleshooter** — guided sequence of checks (local IP, network details, DNS, internet ping, public IP)

### Company Devices
- Maintain a list of company devices (name, address, type, last status)
- Add / remove devices from the UI
- Save / load the device list to local JSON storage
- **Manual Company Network Check** — ping every device and update its status
- **Network Health Summary** — health score and HEALTHY / WARNING / CRITICAL status

### Network Discovery
- Scan the local subnet for active devices
- Improved subnet detection using the local IP **and subnet mask** (not assumed /24)
- Safety cap on subnet size to avoid accidental large scans
- **Known / Unknown device detection** — discovered hosts are matched against your saved device list
- MAC address lookup for discovered devices
- **Stop Discovery** — cancel a running scan at any time

### Internet Quality Test
- Packet loss, average ping, and jitter measurement
- DNS response time measurement
- Download / upload speed (when `speedtest-cli` is installed)
- Gateway vs. internet comparison to isolate where a problem lives
- **Quality score (0–100)** with EXCELLENT / GOOD / WARNING / BAD status
- **Smart Diagnosis** — plain-language explanation of the likely problem
- **Recommended Actions** — concrete next steps for the technician

### Dashboard & Reporting
- Modern dashboard UI: sidebar navigation, header status chips, stat cards
- Live summary cards: total / OK / down / unknown devices, network health, internet quality
- **Automatic daily logs** — every result is appended to a per-day log file
- **Open Logs Folder** — one click to the log directory
- **Save Report** — export the current results console to a text file

## Code Structure

```
gui_app.py           Tkinter dashboard UI and application orchestration
network_tools.py     Core checks: ping, ports, DNS, local/public IP, parsing
discovery.py         Subnet detection, scan planning, host discovery, MAC lookup
internet_quality.py  Quality test, scoring, smart diagnosis, recommended actions
devices_manager.py   Load/save of the company device list (JSON)
logger_utils.py      Automatic daily log files
```

The UI layer (`gui_app.py`) contains no networking logic; all checks live in the dedicated modules and run in background threads so the interface stays responsive.

## Requirements

- **Windows 10 / 11** — the app uses Windows commands (`ping -n`, `ipconfig`, `tracert`, `arp`)
- **Python 3.9+** with Tkinter (included in the standard Windows Python installer)
- No third-party packages are required for core functionality

## How to Run

```
python gui_app.py
```

That's it — the dashboard opens, and all tools are available from the sidebar.

### Optional: speed test support

Download/upload speed measurement in the Internet Quality Test is optional. To enable it:

```
py -m pip install speedtest-cli
```

Without it, the quality test still runs (packet loss, ping, jitter, DNS) and simply reports speed as not available.

## Logs

Every tool result is automatically appended to a daily log file in the `logs/` folder next to the app:

```
logs/network_log_YYYY-MM-DD.txt
```

Each line is timestamped, giving you a free audit trail of every check performed that day. The folder is created automatically and is excluded from version control.

## Company Devices Storage

The device list is stored in `devices.json` next to the app — a plain JSON list of objects with `name`, `address`, `type`, and `last_status` fields. It is written only when you click **Save Devices** and read when you click **Load Devices** (and once at startup).

`devices.json` is **excluded from version control** via `.gitignore`, because it contains your local network's device names and addresses. Each machine keeps its own copy.

## Safety Note

This tool performs network scans (ping sweeps, port checks, host discovery). **Use it only on networks you own or are explicitly authorized to test.** Scanning networks without permission may violate company policy or local law. The built-in subnet size cap and stop button exist to keep scans deliberate and controlled.

## Version History

| Version | Milestone |
|---|---|
| 0.1 | Initial single-window tool: ping, port check, DNS lookup, local/public IP |
| 0.2 | Traceroute, DHCP information, multi-port scanner, full host check, internet troubleshooter |
| 0.3 | Automatic daily logs, save report, open logs folder |
| 0.4 | Company devices list with add/remove, save/load, manual network check, health summary |
| 0.5 | Network discovery with subnet-mask-aware scanning, known/unknown detection, stop discovery; refactor into modules |
| **0.6** | **Internet Quality Test (packet loss, jitter, DNS timing, speed, smart diagnosis, recommended actions) and modern dashboard UI (sidebar navigation, status cards, results console)** |

## Roadmap

| Version | Theme | Planned contents |
|---|---|---|
| **v0.7** | Reporting & polish | CSV export and printable HTML company report; discovery results table with "Add to Company Devices"; results console severity colors |
| **v0.8** | Monitoring & alerts | Settings page; automatic monitoring on an interval; alerts when a device goes DOWN; progress bars; graceful shutdown |
| **v0.9** | History & insight | Device status history with uptime percentages; device detail view; dashboard trends; scoped security exposure check for saved devices |
| **v1.0** | Productization | App icon and About dialog; packaging readiness; test coverage for core modules; final documentation pass |

EXE packaging and an installer are planned **after** v1.0.

## License

Not yet specified. Until a license is added, all rights are reserved by the author.
