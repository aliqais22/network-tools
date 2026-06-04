<img width="1917" height="1034" alt="צילום מסך 2026-06-04 212448" src="https://github.com/user-attachments/assets/239790db-373e-4518-a982-7c347bcafe33" />


# Smart Internet Troubleshooter

Smart Internet Troubleshooter is a Windows Python GUI application for basic network troubleshooting, company device checking, and local network discovery.

The app is built with Python and Tkinter.  
It helps users run common network checks from a graphical interface instead of typing commands manually in the terminal.

## Current Status

Development version.

The project is currently a Python GUI application.  
EXE build and installer will be added later after the main features are completed and tested.

## Features

### Basic Network Tools

- Ping Host
- TCP Port Check
- DNS Lookup
- Local IP Check
- DHCP Information
- Public IP Lookup
- Traceroute
- Multi-Port Scanner
- Full Host Check
- Internet Troubleshooter

### Reports and Logs

- Save Report
- Automatic Daily Logs
- Open Logs Folder

### Company Devices

- Add company devices
- Remove selected device
- Save devices locally
- Load devices automatically
- Check all company devices manually
- Device status: OK / DOWN
- Color device rows by status

### Network Health Summary

- Total devices count
- OK devices count
- DOWN devices count
- Network Health Score percentage
- Network status:
  - HEALTHY
  - WARNING
  - CRITICAL
- Last check time
- List of down/problem devices

### Network Discovery

- Discover devices on the local network
- Scan the local subnet manually
- Show discovery progress
- Stop discovery safely
- Prevent multiple discovery scans at the same time
- Compare discovered devices with saved company devices
- Mark discovered devices as KNOWN or UNKNOWN
- Print discovery summary in the Results box
- Save discovery results automatically in logs

## Logs

The application automatically creates a `logs` folder next to `gui_app.py`.

Each day, a new log file is created using this format:

```text
logs/network_log_YYYY-MM-DD.txt
```

Every line printed in the Results box is also saved in the daily log file with a timestamp.

## Company Devices Storage

Company devices are saved locally in:

```text
devices.json
```

This file is created after saving company devices from the app.

Important:  
Do not upload real company device information to GitHub.  
It is recommended to keep `devices.json` inside `.gitignore`.

## Requirements

- Windows
- Python 3
- Tkinter

Tkinter is usually included with Python on Windows.

## How to Run

Open PowerShell inside the project folder and run:

```bash
py gui_app.py
```

or:

```bash
python gui_app.py
```

## Project Structure

```text
network-tools/
│
├── gui_app.py
├── main.py
├── README.md
├── .gitignore
├── devices.json        # Created locally after saving devices
└── logs/               # Created automatically, not uploaded to GitHub
```

## Recommended .gitignore

```gitignore
__pycache__/
*.pyc
logs/
devices.json
dist/
build/
*.spec
.env
```

## Important Notes

This tool is designed for personal learning, basic troubleshooting, and authorized company/local network diagnostics.

Some features use Windows commands such as:

- ping
- ipconfig
- tracert
- arp

Because of that, the app is currently focused on Windows.

Network discovery and device checking should only be used on networks you own or have permission to test.

## Version History

### v0.4 - Network Discovery and Unknown Device Detection

Added manual local network discovery.

New features:

- Discover devices on the local network
- Scan the local subnet manually
- Show discovery progress
- Stop discovery safely using Stop Discovery
- Prevent multiple discovery scans at the same time
- Compare discovered devices with saved company devices
- Mark devices as KNOWN or UNKNOWN
- Print discovery summary in the Results box
- Save discovery results automatically in daily logs

This version makes the app more useful for small company network auditing by helping detect unknown devices on the local network.

### v0.3 - Manual Network Health Summary

Added manual network health summary after checking company devices.

New features:

- Show total number of devices
- Show number of OK devices
- Show number of DOWN devices
- Calculate Network Health Score percentage
- Show network status as HEALTHY, WARNING, or CRITICAL
- Show last check time
- List DOWN devices in the Results box
- Update a Network Health label in the GUI
- Color device rows by status using table tags
- Save summary results automatically in daily logs

This version improves the manual company network check and makes the app more useful for small company network diagnostics.

### v0.2 - Company Devices List

Added a company devices management feature.

New features:

- Add company devices with name, IP address/host, and device type
- Show devices in a table
- Save devices locally in `devices.json`
- Load saved devices automatically when the app starts
- Remove selected device
- Check all company devices with one click
- Update device status as OK or DOWN
- Print company network check results in the Results box
- Save company check results automatically in the daily logs

This version turns the app from a single-host troubleshooting tool into a basic company network checking tool.

### v0.1 - Basic GUI + Logs

Initial Python GUI version.

Features:

- Ping Host
- TCP Port Check
- DNS Lookup
- Local IP Check
- DHCP Information
- Public IP Lookup
- Traceroute
- Multi-Port Scanner
- Full Host Check
- Internet Troubleshooter
- Save Report
- Automatic Daily Logs
- Open Logs Folder

## Future Plans

- Manual Security Exposure Check
- Export Company Report
- Export CSV / Excel Report
- Export PDF Report
- Device History
- Alerts when a device is DOWN
- Auto Monitoring
- Better dashboard design
- EXE build
- Installer with icon
- Smarter troubleshooting suggestions
### v0.4.1 - Improved Subnet Detection

Improved Network Discovery to detect the real local subnet from the active Windows network adapter.

New improvements:
- Supports private LAN ranges:
  - 10.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
- Detects local IPv4 address, subnet mask, and default gateway
- Calculates the real scan range using the subnet mask
- Prevents scanning very large networks
- Example: 10.0.0.2 with subnet mask 255.255.255.0 scans 10.0.0.1 to 10.0.0.254

## Version

Current version: v0.4 - Network Discovery and Unknown Device Detection

<img width="3763" height="5138" alt="NotebookLM Mind Map (1)" src="https://github.com/user-attachments/assets/cb6bc5ca-0a3d-4bae-a560-2bf86628a737" />

