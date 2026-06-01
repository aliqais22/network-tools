# Smart Internet Troubleshooter

Smart Internet Troubleshooter is a simple Windows network troubleshooting tool built with Python and Tkinter.

The app helps users run basic network checks from a graphical interface instead of typing commands manually in the terminal.

## Current Status

Development version.

The project is currently a Python GUI application.
EXE build and installer will be added later after the main features are completed.

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

## Logs

The application automatically creates a `logs` folder next to `gui_app.py`.

Each day, a new log file is created using this format:

```text
logs/network_log_YYYY-MM-DD.txt
