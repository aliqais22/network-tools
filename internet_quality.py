import socket
import subprocess
import time

import discovery
from network_tools import format_ms_value, parse_ping_quality_output


def run_speed_test():
    try:
        import speedtest
    except ImportError:
        return {"available": False, "failed": False, "download_mbps": None, "upload_mbps": None, "error": None}

    try:
        tester = speedtest.Speedtest()
        tester.get_best_server()
        download_mbps = tester.download() / 1_000_000
        upload_mbps = tester.upload() / 1_000_000
        return {
            "available": True,
            "failed": False,
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "error": None,
        }
    except Exception as error:
        return {
            "available": True,
            "failed": True,
            "download_mbps": None,
            "upload_mbps": None,
            "error": str(error),
        }


def run_quality_ping(target, count):
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), "-w", "1000", target],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=count + 10,
        )
        return parse_ping_quality_output(f"{result.stdout}\n{result.stderr}", count), None
    except FileNotFoundError:
        return None, "ERROR: The Windows ping command was not found."
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode("utf-8", errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode("utf-8", errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        warning = f"WARNING: Ping test to {target} timed out before all replies were received."
        return parse_ping_quality_output(f"{stdout}\n{stderr}", count), warning


def ping_is_ok(metrics):
    return metrics is not None and metrics["packets_received"] > 0 and metrics["packet_loss_percent"] <= 2


def ping_failed_or_high_loss(metrics):
    return metrics is None or metrics["packets_received"] == 0 or metrics["packet_loss_percent"] > 5


def calculate_score(packet_loss_percent, avg_ping, jitter, dns_response_ms, download_mbps=None, upload_mbps=None):
    score = 100 - (packet_loss_percent * 5)

    if avg_ping is None:
        score -= 30
    elif avg_ping > 150:
        score -= 30
    elif avg_ping > 100:
        score -= 20
    elif avg_ping > 50:
        score -= 10

    if jitter is not None:
        if jitter > 60:
            score -= 20
        elif jitter > 30:
            score -= 10

    if dns_response_ms is None:
        score -= 10
    elif dns_response_ms > 500:
        score -= 20
    elif dns_response_ms > 200:
        score -= 10

    if download_mbps is not None:
        if download_mbps < 3:
            score -= 30
        elif download_mbps < 10:
            score -= 15

    if upload_mbps is not None:
        if upload_mbps < 1:
            score -= 30
        elif upload_mbps < 3:
            score -= 15

    return max(0, min(100, score))


def get_status(score):
    if score >= 90:
        return "EXCELLENT"
    if score >= 75:
        return "GOOD"
    if score >= 50:
        return "WARNING"
    return "BAD"


def build_diagnosis(gateway_metrics, internet_metrics, domain_metrics, dns_response_ms, dns_failed, speed_results):
    diagnoses = []
    categories = set()

    if ping_failed_or_high_loss(gateway_metrics):
        diagnoses.append("Problem likely inside the local network, Wi-Fi, network adapter, or router.")
        categories.add("local")
    elif ping_is_ok(gateway_metrics) and ping_failed_or_high_loss(internet_metrics):
        diagnoses.append("Problem likely with the internet connection, ISP, modem, or WAN link.")
        categories.add("isp")

    if ping_is_ok(internet_metrics) and (ping_failed_or_high_loss(domain_metrics) or dns_failed):
        diagnoses.append("Problem likely related to DNS.")
        categories.add("dns")

    if gateway_metrics is not None and gateway_metrics["avg_ping"] is not None and gateway_metrics["avg_ping"] > 50:
        diagnoses.append(
            "Local network latency is high. Possible causes: weak Wi-Fi signal, overloaded router, or local network congestion."
        )
        categories.add("local")

    if internet_metrics is not None:
        internet_loss = internet_metrics["packet_loss_percent"]
        if 2 <= internet_loss <= 5:
            diagnoses.append("Minor packet loss detected. This may affect video calls, gaming, VoIP, or live systems.")
            categories.add("packet_loss")
        elif internet_loss > 5:
            diagnoses.append("High packet loss detected. Internet connection is unstable.")
            categories.add("packet_loss")

    if dns_response_ms is not None and dns_response_ms > 200:
        diagnoses.append("DNS response is slow. Consider changing DNS server or checking router DNS settings.")
        categories.add("dns")

    if not speed_results["available"]:
        categories.add("speed_unavailable")
    elif speed_results["failed"]:
        diagnoses.append(
            "Speed test failed. This may be caused by blocked speedtest servers, firewall, or temporary internet issue."
        )
        categories.add("speed_failed")
    else:
        download_mbps = speed_results["download_mbps"]
        upload_mbps = speed_results["upload_mbps"]
        if download_mbps is not None and download_mbps < 10:
            diagnoses.append("Download speed is low. This may affect browsing, streaming, updates, and cloud services.")
            categories.add("low_download")
        if upload_mbps is not None and upload_mbps < 3:
            diagnoses.append(
                "Upload speed is low. This may affect video calls, file uploads, cloud backup, and cameras."
            )
            categories.add("low_upload")

    if not diagnoses:
        diagnoses.append(
            "Internet connection looks stable. No major gateway, DNS, latency, jitter, or packet loss issues detected."
        )
        categories.add("good")

    return diagnoses, categories


def build_recommended_actions(categories):
    actions = []

    if "dns" in categories:
        actions.extend(["Try changing DNS to 8.8.8.8 or 1.1.1.1.", "Check router DNS settings."])

    if "local" in categories:
        actions.extend(["Check Wi-Fi signal.", "Test with Ethernet cable.", "Restart router.", "Check network adapter."])

    if "isp" in categories:
        actions.extend(["Restart modem/router.", "Test from another device.", "Contact ISP if the issue continues."])

    if "packet_loss" in categories:
        actions.extend(
            [
                "Test using Ethernet cable.",
                "Stop heavy downloads.",
                "Check if other devices have the same issue.",
                "Contact ISP if packet loss continues.",
            ]
        )

    if "low_download" in categories:
        actions.append(
            "Restart router, test with Ethernet cable, stop heavy downloads, and compare with your ISP package speed."
        )

    if "low_upload" in categories:
        actions.append(
            "Check if cameras/cloud backup are using upload, test with Ethernet, and compare with your ISP upload package."
        )

    if "speed_unavailable" in categories:
        actions.append("Install speedtest-cli using: py -m pip install speedtest-cli")

    if "good" in categories:
        actions.append("No action needed. The connection quality is excellent.")

    unique_actions = []
    for action in actions:
        if action not in unique_actions:
            unique_actions.append(action)
    return unique_actions


def run_internet_quality_test(progress_callback=None):
    internet_target = "8.8.8.8"
    domain_target = "google.com"
    lines = []

    if progress_callback:
        progress_callback("Running Internet Quality Test...")
    else:
        lines.append("Running Internet Quality Test...")

    adapter = discovery.get_active_network_details()
    gateway = adapter["gateway"] if adapter else None

    gateway_metrics = None
    if gateway:
        gateway_metrics, warning = run_quality_ping(gateway, 10)
        if warning:
            lines.append(warning)

    internet_metrics, warning = run_quality_ping(internet_target, 20)
    if warning:
        lines.append(warning)

    domain_metrics, warning = run_quality_ping(domain_target, 10)
    if warning:
        lines.append(warning)

    dns_response_ms = None
    dns_failed = False
    try:
        dns_start = time.perf_counter()
        socket.gethostbyname(domain_target)
        dns_response_ms = (time.perf_counter() - dns_start) * 1000
    except socket.gaierror:
        dns_failed = True

    if progress_callback:
        progress_callback("Running speed test...")
    speed_results = run_speed_test()

    internet_loss = internet_metrics["packet_loss_percent"] if internet_metrics else 100
    internet_avg_ping = internet_metrics["avg_ping"] if internet_metrics else None
    internet_jitter = internet_metrics["jitter"] if internet_metrics else None
    download_mbps = speed_results["download_mbps"]
    upload_mbps = speed_results["upload_mbps"]
    score = calculate_score(internet_loss, internet_avg_ping, internet_jitter, dns_response_ms, download_mbps, upload_mbps)
    status = get_status(score)
    diagnoses, categories = build_diagnosis(
        gateway_metrics,
        internet_metrics,
        domain_metrics,
        dns_response_ms,
        dns_failed,
        speed_results,
    )
    actions = build_recommended_actions(categories)

    lines.extend(
        [
            "",
            "Internet Quality Test",
            "---------------------",
            f"Gateway: {gateway if gateway else 'Not detected'}",
            f"Gateway Ping: {'Available' if gateway_metrics else 'Not available'}",
        ]
    )

    if gateway_metrics:
        lines.append(f"Gateway Packet Loss: {gateway_metrics['packet_loss_percent']:.0f}%")
        lines.append(f"Gateway Avg Ping: {format_ms_value(gateway_metrics['avg_ping'])}")
    else:
        lines.append("Gateway Packet Loss: Not available")
        lines.append("Gateway Avg Ping: Not available")

    lines.extend(["", f"Internet Target: {internet_target}"])
    if internet_metrics:
        lines.extend(
            [
                f"Packets Sent: {internet_metrics['packets_sent']}",
                f"Packets Received: {internet_metrics['packets_received']}",
                f"Packets Lost: {internet_metrics['packets_lost']}",
                f"Packet Loss: {internet_metrics['packet_loss_percent']:.0f}%",
                f"Min Ping: {format_ms_value(internet_metrics['min_ping'])}",
                f"Max Ping: {format_ms_value(internet_metrics['max_ping'])}",
                f"Avg Ping: {format_ms_value(internet_metrics['avg_ping'])}",
                f"Jitter: {format_ms_value(internet_metrics['jitter'])}",
            ]
        )
    else:
        lines.extend(
            [
                "Packets Sent: 20",
                "Packets Received: 0",
                "Packets Lost: 20",
                "Packet Loss: 100%",
                "Min Ping: Not available",
                "Max Ping: Not available",
                "Avg Ping: Not available",
                "Jitter: Not available",
            ]
        )

    lines.extend(
        [
            "",
            "Domain Test:",
            f"Domain: {domain_target}",
            f"Domain Ping: {'Available' if domain_metrics and domain_metrics['packets_received'] > 0 else 'Failed'}",
            f"DNS Response Time: {format_ms_value(dns_response_ms)}",
            "",
            "Speed Test:",
        ]
    )

    if not speed_results["available"]:
        lines.extend(
            [
                "Speed test is not available. Install it with: py -m pip install speedtest-cli",
                "Download Speed: Not available",
                "Upload Speed: Not available",
            ]
        )
    elif speed_results["failed"]:
        lines.append("Speed test failed. This may be caused by blocked speedtest servers, firewall, or temporary internet issue.")
        if speed_results["error"]:
            lines.append(f"Speed Test Error: {speed_results['error']}")
        lines.extend(["Download Speed: Not available", "Upload Speed: Not available"])
    else:
        lines.append(f"Download Speed: {download_mbps:.2f} Mbps")
        lines.append(f"Upload Speed: {upload_mbps:.2f} Mbps")

    lines.extend(["", f"Internet Quality Score: {score:.0f}/100", f"Status: {status}", "", "Smart Diagnosis:"])
    lines.extend(f"- {diagnosis}" for diagnosis in diagnoses)
    lines.extend(["", "Recommended Actions:"])
    lines.extend(f"- {action}" for action in actions)
    return lines
