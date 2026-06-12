from datetime import datetime
from pathlib import Path


def get_logs_folder(base_file):
    logs_folder = Path(base_file).resolve().parent / "logs"
    logs_folder.mkdir(exist_ok=True)
    return logs_folder


def write_daily_log(logs_folder, text=""):
    logs_folder.mkdir(exist_ok=True)
    log_file = logs_folder / f"network_log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = str(text).splitlines() or [""]

    with log_file.open("a", encoding="utf-8") as file:
        for line in lines:
            file.write(f"[{timestamp}] {line}\n")
