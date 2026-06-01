# Smart Internet Troubleshooter

Smart Internet Troubleshooter is a simple Windows network troubleshooting tool built with Python and Tkinter.

The app helps users run basic network checks from a graphical interface instead of typing commands manually in the terminal.

## Current Status

Development version.

The project is currently a Python GUI application.
EXE build and installer will be added later after the main features are completed.

## Version History

### v0.2 - Company Devices List

Added a company devices management feature.

New features:
- Add company devices with name, IP address/host, and device type
- Show devices in a table
- Save devices locally in `devices.json`
- Load saved devices automatically when the app starts
- Remove selected device
- Check all company devices with one click
- Update device status as `OK` or `DOWN`
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
The application automatically creates a `logs` folder next to `gui_app.py`.
## Features

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
- Company Devices List
- Add / Remove company devices
- Save / Load devices
- Check all company devices
- Device status: OK / DOWN
Each day, a new log file is created using this format:
## Project Structure

```text
network-tools/
│
├── gui_app.py
├── main.py
├── README.md
├── .gitignore
├── devices.json        # Created after saving company devices
└── logs/               # Created automatically, not uploaded to GitHub
```text
logs/network_log_2026.6.1.txt
