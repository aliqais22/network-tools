# network-tools

A beginner-friendly Python CLI Network Tools Dashboard for learning basic networking concepts and practicing Python.

This project uses only built-in Python libraries, so it does not need any extra packages.

## Features

- Ping a host using the Windows `ping` command
- Check whether a TCP port is open using Python sockets
- Look up the IP address for a domain name
- Show the local IP address of your computer
- Simple menu-driven command-line interface

## How to run

1. Open Command Prompt or PowerShell.
2. Go to the project folder:

```powershell
cd C:\Users\USER\network-tools
```

3. Run the program:

```powershell
python main.py
```

If `python` does not work, try:

```powershell
py main.py
```

## Example usage

```text
============================
 Network Tools Dashboard
============================

Choose an option:
1) Ping a host
2) Check if a TCP port is open
3) DNS lookup
4) Show my local IP address
5) Exit

Enter your choice (1-5): 3
Enter a domain name (example: python.org): python.org
python.org resolves to 151.101.64.223
```

Another example:

```text
Enter your choice (1-5): 2
Enter a host (example: example.com): example.com
Enter a TCP port (example: 80): 80

Checking example.com:80...
OPEN: TCP port 80 is open on example.com.
```

## Future improvements

- Add support for saving results to a log file
- Add IPv6 support
- Add a nicer command-line interface with colors
- Add tests for input validation
- Add Linux and macOS ping support
