# Network Tools Dashboard

A beginner-friendly Python networking toolkit that provides multiple network diagnostic tools in one dashboard.

## Project Description

This project is a command-line Network Tools Dashboard written in Python.  
It allows the user to test and analyze network connectivity using tools such as Ping, TCP Port Check, DNS Lookup, Local IP detection, DHCP information, Public IP lookup, Traceroute, Multi-Port Scanner, and Full Host Check.

The project is mainly designed for Windows because it uses Windows networking commands such as:

- ping -n
- ipconfig /all
- tracert

## Features

- Ping Host
- TCP Port Check
- DNS Lookup
- Local IP Detection
- DHCP Information
- Public IP Lookup
- Traceroute
- Multi-Port Scanner
- Generate Network Report
- Full Host Check

## Full Host Check Feature

The Full Host Check is an advanced feature that performs a complete diagnosis for a target host.

It checks:

- DNS resolution
- Ping connectivity
- HTTP port 80
- HTTPS port 443
- Common TCP ports
- Traceroute
- Final diagnosis summary
- Network Health Score

This feature combines multiple tools into one complete test, making the project more useful and professional.

## Common Ports Scanned

| Port | Service |
|------|---------|
| 21 | FTP |
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 110 | POP3 |
| 143 | IMAP |
| 443 | HTTPS |
| 3306 | MySQL |
| 3389 | Remote Desktop |

## How to Run

Make sure Python is installed on your computer.

Run the program using:

```bash
python main.py
