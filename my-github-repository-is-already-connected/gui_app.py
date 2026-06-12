import os
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from tkinter import END, filedialog, messagebox, scrolledtext, ttk
import tkinter as tk

import devices_manager
import discovery
import internet_quality
import logger_utils
import network_tools
from network_tools import DEFAULT_SCAN_PORTS, PING_COUNT, PING_TIMEOUT_MS


APP_TITLE = "Smart Internet Troubleshooter"
APP_SUBTITLE = "IT Network Monitoring & Troubleshooting Console"


class SmartInternetTroubleshooter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x860")
        self.minsize(1040, 700)

        self.host_var = tk.StringVar(value="google.com")
        self.port_var = tk.StringVar(value="80")
        self.scan_ports_var = tk.StringVar(value=DEFAULT_SCAN_PORTS)
        self.status_var = tk.StringVar(value="Ready")
        self.device_name_var = tk.StringVar()
        self.device_address_var = tk.StringVar()
        self.device_type_var = tk.StringVar(value="Router")
        self.network_health_var = tk.StringVar(value="Network Health: Not checked")
        self.network_health_score_var = tk.StringVar(value="--")
        self.network_health_status_var = tk.StringVar(value="Not checked")
        self.internet_quality_var = tk.StringVar(value="Internet Quality: Not tested")
        self.internet_quality_score_var = tk.StringVar(value="--")
        self.total_devices_var = tk.StringVar(value="0")
        self.ok_devices_var = tk.StringVar(value="0")
        self.down_devices_var = tk.StringVar(value="0")
        self.unknown_devices_var = tk.StringVar(value="0")
        self.active_devices_var = tk.StringVar(value="0 / 0")
        self.last_scan_var = tk.StringVar(value="Last scan: Never")
        self.discovery_progress_var = tk.StringVar(value="Discovery: Not started")
        self.discovery_found_var = tk.StringVar(value="--")
        self.discovery_known_var = tk.StringVar(value="--")
        self.discovery_unknown_var = tk.StringVar(value="--")
        self.last_discovery_summary_var = tk.StringVar(value="Last discovery: Not run yet")
        self.iq_download_var = tk.StringVar(value="Not tested")
        self.iq_upload_var = tk.StringVar(value="Not tested")
        self.iq_packet_loss_var = tk.StringVar(value="Not tested")
        self.iq_avg_ping_var = tk.StringVar(value="Not tested")
        self.iq_jitter_var = tk.StringVar(value="Not tested")
        self.iq_dns_var = tk.StringVar(value="Not tested")
        self.iq_score_var = tk.StringVar(value="--")
        self.iq_status_var = tk.StringVar(value="Not tested")
        self.discovery_running = False
        self.discovery_cancel_event = threading.Event()
        self.logs_folder = logger_utils.get_logs_folder(__file__)
        self.devices_file = devices_manager.get_devices_file(__file__)
        self.pages = {}
        self.nav_buttons = {}
        self.current_page = None

        self._configure_styles()
        self.configure(bg=self.colors["bg"])
        self.status_var.trace_add("write", self._update_status_indicator)
        self._build_window()

    # ------------------------------------------------------------------
    # Theme and shared widget helpers
    # ------------------------------------------------------------------
    def _configure_styles(self):
        self.colors = {
            "bg": "#eef1f5",
            "card": "#ffffff",
            "tile": "#f8fafc",
            "border": "#d7dde6",
            "chip_bg": "#f1f5f9",
            "sidebar": "#1f2a3a",
            "sidebar_hover": "#28374c",
            "sidebar_active": "#2e3f57",
            "sidebar_text": "#cbd5e1",
            "sidebar_text_active": "#ffffff",
            "sidebar_muted": "#8294ab",
            "text": "#1e293b",
            "muted": "#64748b",
            "green": "#15803d",
            "green_bg": "#e7f8ee",
            "orange": "#b45309",
            "orange_bg": "#fdf3d8",
            "red": "#b91c1c",
            "red_bg": "#fdeaea",
            "blue": "#1d4ed8",
            "blue_bg": "#dbeafe",
            "slate": "#334155",
            "console_bg": "#101725",
            "console_fg": "#d7e0ee",
        }

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Tool.TButton",
            background="#ffffff",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            focusthickness=1,
            focuscolor=self.colors["blue"],
            padding=(12, 7),
        )
        style.map(
            "Tool.TButton",
            background=[("active", "#e8eef7"), ("disabled", "#f3f4f6")],
            foreground=[("disabled", "#9aa4b2")],
        )
        style.configure(
            "Accent.TButton",
            background="#2563eb",
            foreground="#ffffff",
            bordercolor="#1d4ed8",
            focusthickness=1,
            focuscolor="#1e3a8a",
            padding=(12, 7),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#1d4ed8"), ("disabled", "#a8c0f0")],
            foreground=[("disabled", "#f0f4ff")],
        )
        style.configure(
            "Danger.TButton",
            background="#dc2626",
            foreground="#ffffff",
            bordercolor="#b91c1c",
            focusthickness=1,
            focuscolor="#7f1d1d",
            padding=(12, 7),
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#b91c1c"), ("disabled", "#f3f4f6")],
            foreground=[("disabled", "#9aa4b2")],
        )
        style.configure(
            "Light.TEntry",
            fieldbackground="#ffffff",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            insertcolor=self.colors["text"],
        )
        style.configure(
            "Light.TCombobox",
            fieldbackground="#ffffff",
            background="#ffffff",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            arrowcolor=self.colors["muted"],
        )
        style.map(
            "Light.TCombobox",
            fieldbackground=[("readonly", "#ffffff")],
            foreground=[("readonly", self.colors["text"])],
        )
        style.configure(
            "Light.Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            rowheight=28,
        )
        style.configure(
            "Light.Treeview.Heading",
            background="#eef2f7",
            foreground="#475569",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "Light.Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")],
        )

        self.option_add("*TCombobox*Listbox.background", "#ffffff")
        self.option_add("*TCombobox*Listbox.foreground", self.colors["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", "#2563eb")
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    def _card(self, parent, bg=None):
        return tk.Frame(
            parent,
            bg=bg or self.colors["card"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            bd=0,
        )

    def _tk_label(self, parent, text="", textvariable=None, bg=None, fg=None, font=None, anchor=tk.W):
        return tk.Label(
            parent,
            text=text,
            textvariable=textvariable,
            bg=bg or parent.cget("bg"),
            fg=fg or self.colors["text"],
            font=font or ("Segoe UI", 9),
            anchor=anchor,
        )

    def _section_title(self, parent, text):
        return self._tk_label(parent, text=text, font=("Segoe UI", 11, "bold"))

    def _muted_label(self, parent, text="", textvariable=None):
        return self._tk_label(parent, text=text, textvariable=textvariable, fg=self.colors["muted"])

    def _tool_button(self, parent, text, command, style="Tool.TButton"):
        return ttk.Button(parent, text=text, command=command, style=style)

    def _stat_card(self, parent, title, value_var, accent, column, last=False):
        card = self._card(parent)
        card.grid(row=0, column=column, sticky=tk.NSEW, padx=(0, 0 if last else 10))
        card.columnconfigure(0, weight=1)
        tk.Frame(card, bg=accent, height=3).grid(row=0, column=0, sticky=tk.EW)
        self._tk_label(
            card,
            text=title.upper(),
            fg=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=1, column=0, sticky=tk.W, padx=14, pady=(10, 1))
        value = self._tk_label(card, textvariable=value_var, fg=accent, font=("Segoe UI", 19, "bold"))
        value.grid(row=2, column=0, sticky=tk.W, padx=14, pady=(0, 10))
        return card, value

    def _metric_tile(self, parent, title, value_var, row, column, last_in_row=False):
        tile = tk.Frame(
            parent,
            bg=self.colors["tile"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
        )
        tile.grid(row=row, column=column, sticky=tk.NSEW, padx=(0, 0 if last_in_row else 8), pady=(0, 8))
        tile.columnconfigure(0, weight=1)
        self._tk_label(
            tile,
            text=title.upper(),
            fg=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky=tk.W, padx=12, pady=(8, 1))
        value = self._tk_label(tile, textvariable=value_var, font=("Segoe UI", 11, "bold"))
        value.grid(row=1, column=0, sticky=tk.W, padx=12, pady=(0, 8))
        return value

    def _header_chip(self, parent):
        chip = tk.Frame(
            parent,
            bg=self.colors["chip_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1,
        )
        chip.pack(side=tk.LEFT, padx=(8, 0))
        return chip

    def _create_page(self, key):
        page = tk.Frame(self.pages_host, bg=self.colors["bg"])
        page.grid(row=0, column=0, sticky=tk.NSEW)
        page.columnconfigure(0, weight=1)
        self.pages[key] = page
        return page

    def _page_header(self, page, title, subtitle):
        header = tk.Frame(page, bg=self.colors["bg"])
        header.grid(row=0, column=0, sticky=tk.EW, pady=(0, 12))
        header.columnconfigure(0, weight=1)
        self._tk_label(header, text=title, font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky=tk.W)
        self._muted_label(header, text=subtitle).grid(row=1, column=0, sticky=tk.W, pady=(1, 0))
        return header

    def _set_text_widget(self, widget, lines):
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", END)
        widget.insert(END, "\n".join(f"• {line}" for line in lines))
        widget.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Window construction
    # ------------------------------------------------------------------
    def _build_window(self):
        self.build_header()

        shell = tk.Frame(self, bg=self.colors["bg"])
        shell.pack(fill=tk.BOTH, expand=True)

        self.build_sidebar(shell)

        content = tk.Frame(shell, bg=self.colors["bg"])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=16)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=5)
        content.rowconfigure(1, weight=3)

        self.pages_host = tk.Frame(content, bg=self.colors["bg"])
        self.pages_host.grid(row=0, column=0, sticky=tk.NSEW)
        self.pages_host.rowconfigure(0, weight=1)
        self.pages_host.columnconfigure(0, weight=1)

        self.build_dashboard_section()
        self.build_network_tools_section()
        self.build_company_devices_section()
        self.build_discovery_section()
        self.build_internet_quality_section()
        self.build_logs_section()
        self.build_results_section(content)

        self.show_page("dashboard")
        self.write_line("Welcome. Use the sidebar to open a section, then run a tool. All output appears in the Results Console.")
        self.load_devices(show_message=False)
        self.refresh_dashboard_stats()

    def build_header(self):
        header = tk.Frame(self, bg=self.colors["card"])
        header.pack(side=tk.TOP, fill=tk.X)

        inner = tk.Frame(header, bg=self.colors["card"])
        inner.pack(fill=tk.X, padx=18, pady=10)

        brand = tk.Frame(inner, bg=self.colors["card"])
        brand.pack(side=tk.LEFT)
        logo = tk.Label(
            brand,
            text="ST",
            bg="#2563eb",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            width=3,
        )
        logo.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        titles = tk.Frame(brand, bg=self.colors["card"])
        titles.pack(side=tk.LEFT)
        self._tk_label(titles, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)
        self._muted_label(titles, text=APP_SUBTITLE).pack(anchor=tk.W)

        chips = tk.Frame(inner, bg=self.colors["card"])
        chips.pack(side=tk.RIGHT)

        status_chip = self._header_chip(chips)
        self.status_dot_label = self._tk_label(status_chip, text="●", fg=self.colors["green"], font=("Segoe UI", 9))
        self.status_dot_label.pack(side=tk.LEFT, padx=(10, 4), pady=6)
        self._tk_label(status_chip, textvariable=self.status_var, font=("Segoe UI", 9, "bold")).pack(
            side=tk.LEFT, padx=(0, 10), pady=6
        )

        health_chip = self._header_chip(chips)
        self.network_health_top_label = self._tk_label(
            health_chip,
            textvariable=self.network_health_var,
            fg=self.colors["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.network_health_top_label.pack(side=tk.LEFT, padx=10, pady=6)

        quality_chip = self._header_chip(chips)
        self.internet_quality_top_label = self._tk_label(
            quality_chip,
            textvariable=self.internet_quality_var,
            fg=self.colors["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.internet_quality_top_label.pack(side=tk.LEFT, padx=10, pady=6)

        tk.Frame(self, bg=self.colors["border"], height=1).pack(side=tk.TOP, fill=tk.X)

    def build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.colors["sidebar"], width=208)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        self._tk_label(
            sidebar,
            text="NAVIGATION",
            bg=self.colors["sidebar"],
            fg=self.colors["sidebar_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor=tk.W, padx=18, pady=(16, 6))

        nav_items = [
            ("dashboard", "Dashboard"),
            ("tools", "Network Tools"),
            ("devices", "Company Devices"),
            ("discovery", "Network Discovery"),
            ("quality", "Internet Quality"),
            ("logs", "Logs / Reports"),
        ]
        for key, text in nav_items:
            button = tk.Button(
                sidebar,
                text=text,
                command=lambda page=key: self.show_page(page),
                bg=self.colors["sidebar"],
                fg=self.colors["sidebar_text"],
                activebackground=self.colors["sidebar_active"],
                activeforeground=self.colors["sidebar_text_active"],
                relief=tk.FLAT,
                bd=0,
                anchor=tk.W,
                padx=16,
                pady=8,
                font=("Segoe UI", 10),
                cursor="hand2",
            )
            button.pack(fill=tk.X, padx=8, pady=1)
            button.bind("<Enter>", lambda _event, page=key: self._nav_hover(page, True))
            button.bind("<Leave>", lambda _event, page=key: self._nav_hover(page, False))
            self.nav_buttons[key] = button

        footer = tk.Frame(sidebar, bg=self.colors["sidebar"])
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=14)
        self._tk_label(
            footer,
            text="Version 1.0",
            bg=self.colors["sidebar"],
            fg=self.colors["sidebar_muted"],
            font=("Segoe UI", 8),
        ).pack(anchor=tk.W)
        self._tk_label(
            footer,
            text="Windows Network Monitor",
            bg=self.colors["sidebar"],
            fg=self.colors["sidebar_muted"],
            font=("Segoe UI", 8),
        ).pack(anchor=tk.W, pady=(2, 0))

    def _nav_hover(self, key, entering):
        if key == self.current_page:
            return
        button = self.nav_buttons.get(key)
        if button is not None:
            button.configure(bg=self.colors["sidebar_hover"] if entering else self.colors["sidebar"])

    def show_page(self, key):
        page = self.pages.get(key)
        if page is None:
            return
        self.current_page = key
        page.tkraise()
        for name, button in self.nav_buttons.items():
            active = name == key
            button.configure(
                bg=self.colors["sidebar_active"] if active else self.colors["sidebar"],
                fg=self.colors["sidebar_text_active"] if active else self.colors["sidebar_text"],
            )
        if key == "dashboard":
            self.refresh_dashboard_stats()

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    def build_dashboard_section(self):
        page = self._create_page("dashboard")
        header = self._page_header(page, "Dashboard", "Network status overview at a glance.")
        self._tool_button(header, "Refresh", self.refresh_dashboard_stats, "Accent.TButton").grid(
            row=0, column=1, rowspan=2, sticky=tk.E
        )

        self.build_dashboard_cards(page, row=1)

        body = tk.Frame(page, bg=self.colors["bg"])
        body.grid(row=2, column=0, sticky=tk.NSEW)
        page.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        overview = self._card(body)
        overview.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        overview.columnconfigure(0, weight=1)
        self._section_title(overview, "Status Overview").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 8))
        overview_rows = [
            self.network_health_var,
            self.internet_quality_var,
            self.last_scan_var,
            self.discovery_progress_var,
        ]
        for index, variable in enumerate(overview_rows, start=1):
            self._tk_label(overview, textvariable=variable).grid(
                row=index, column=0, sticky=tk.W, padx=14, pady=(0, 6)
            )
        active_row = tk.Frame(overview, bg=self.colors["card"])
        active_row.grid(row=len(overview_rows) + 1, column=0, sticky=tk.W, padx=14, pady=(0, 12))
        self._muted_label(active_row, text="Active devices (OK / Total):").pack(side=tk.LEFT)
        self._tk_label(active_row, textvariable=self.active_devices_var, font=("Segoe UI", 9, "bold")).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        actions = self._card(body)
        actions.grid(row=0, column=1, sticky=tk.NSEW)
        actions.columnconfigure(0, weight=1)
        self._section_title(actions, "Quick Actions").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 2))
        self._muted_label(actions, text="Run the most common daily checks.").grid(
            row=1, column=0, sticky=tk.W, padx=14, pady=(0, 8)
        )
        quick_actions = [
            ("Check Company Network", self.check_company_network, "Accent.TButton"),
            ("Internet Quality Test", self.internet_quality_test, "Tool.TButton"),
            ("Internet Troubleshooter", self.internet_troubleshooter, "Tool.TButton"),
            ("Open Logs Folder", self.open_logs_folder, "Tool.TButton"),
        ]
        for index, (text, command, style) in enumerate(quick_actions):
            last = index == len(quick_actions) - 1
            self._tool_button(actions, text, command, style).grid(
                row=2 + index, column=0, sticky=tk.EW, padx=14, pady=(0, 14 if last else 6)
            )

    def build_dashboard_cards(self, page, row):
        cards = tk.Frame(page, bg=self.colors["bg"])
        cards.grid(row=row, column=0, sticky=tk.EW, pady=(0, 12))
        specs = [
            ("Total Devices", self.total_devices_var, self.colors["slate"]),
            ("OK Devices", self.ok_devices_var, self.colors["green"]),
            ("Down Devices", self.down_devices_var, self.colors["red"]),
            ("Unknown Devices", self.unknown_devices_var, self.colors["orange"]),
            ("Network Health", self.network_health_score_var, self.colors["green"]),
            ("Internet Quality", self.internet_quality_score_var, self.colors["blue"]),
        ]
        for column in range(len(specs)):
            cards.columnconfigure(column, weight=1, uniform="dash_cards")
        for column, (title, variable, accent) in enumerate(specs):
            _, value_label = self._stat_card(cards, title, variable, accent, column, last=column == len(specs) - 1)
            if title == "Network Health":
                self.network_health_card_value = value_label
            elif title == "Internet Quality":
                self.internet_quality_card_value = value_label

    def build_network_tools_section(self):
        page = self._create_page("tools")
        self._page_header(page, "Network Tools", "Manual Windows-focused checks. Output appears in the Results Console.")

        inputs = self._card(page)
        inputs.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        inputs.columnconfigure(1, weight=3)
        inputs.columnconfigure(3, weight=1)
        inputs.columnconfigure(5, weight=3)
        self._section_title(inputs, "Target").grid(row=0, column=0, columnspan=6, sticky=tk.W, padx=14, pady=(12, 8))

        self._muted_label(inputs, text="Host / Domain").grid(row=1, column=0, sticky=tk.W, padx=(14, 8), pady=(0, 12))
        ttk.Entry(inputs, textvariable=self.host_var, style="Light.TEntry").grid(
            row=1, column=1, sticky=tk.EW, padx=(0, 14), pady=(0, 12)
        )
        self._muted_label(inputs, text="Port").grid(row=1, column=2, sticky=tk.W, padx=(0, 8), pady=(0, 12))
        ttk.Entry(inputs, textvariable=self.port_var, width=10, style="Light.TEntry").grid(
            row=1, column=3, sticky=tk.EW, padx=(0, 14), pady=(0, 12)
        )
        self._muted_label(inputs, text="Multi-Port List").grid(row=1, column=4, sticky=tk.W, padx=(0, 8), pady=(0, 12))
        ttk.Entry(inputs, textvariable=self.scan_ports_var, style="Light.TEntry").grid(
            row=1, column=5, sticky=tk.EW, padx=(0, 14), pady=(0, 12)
        )

        groups_frame = tk.Frame(page, bg=self.colors["bg"])
        groups_frame.grid(row=2, column=0, sticky=tk.NSEW)
        page.rowconfigure(2, weight=1)
        groups_frame.rowconfigure(0, weight=1)
        for column in range(3):
            groups_frame.columnconfigure(column, weight=1, uniform="tool_groups")

        groups = [
            (
                "Connectivity",
                "Reachability and routing checks.",
                [
                    ("Ping Host", self.ping_host, False),
                    ("Traceroute", self.traceroute, False),
                    ("TCP Port Check", self.tcp_port_check, False),
                    ("Multi-Port Scanner", self.multi_port_scanner, False),
                ],
            ),
            (
                "Addressing & DNS",
                "IP configuration and name resolution.",
                [
                    ("DNS Lookup", self.dns_lookup, False),
                    ("Local IP", self.local_ip, False),
                    ("DHCP Information", self.dhcp_information, False),
                    ("Public IP Lookup", self.public_ip_lookup, False),
                ],
            ),
            (
                "Diagnostics",
                "Combined health and quality checks.",
                [
                    ("Full Host Check", self.full_host_check, False),
                    ("Internet Troubleshooter", self.internet_troubleshooter, True),
                    ("Internet Quality Test", self.internet_quality_test, True),
                ],
            ),
        ]
        for column, (title, subtitle, buttons) in enumerate(groups):
            card = self._card(groups_frame)
            card.grid(row=0, column=column, sticky=tk.NSEW, padx=(0, 12 if column < len(groups) - 1 else 0))
            card.columnconfigure(0, weight=1)
            self._section_title(card, title).grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 2))
            self._muted_label(card, text=subtitle).grid(row=1, column=0, sticky=tk.W, padx=14, pady=(0, 8))
            for index, (text, command, accent) in enumerate(buttons):
                style = "Accent.TButton" if accent else "Tool.TButton"
                self._tool_button(card, text, command, style).grid(
                    row=2 + index, column=0, sticky=tk.EW, padx=14, pady=(0, 6)
                )

    def build_company_devices_section(self):
        page = self._create_page("devices")
        header = self._page_header(
            page, "Company Devices", "Maintain the monitored device list and run manual network checks."
        )
        self.network_health_panel_label = self._tk_label(
            header,
            textvariable=self.network_health_var,
            fg=self.colors["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.network_health_panel_label.grid(row=0, column=1, rowspan=2, sticky=tk.E)

        form = self._card(page)
        form.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        form.columnconfigure(1, weight=3)
        form.columnconfigure(3, weight=3)
        form.columnconfigure(5, weight=2)
        self._section_title(form, "Add Device").grid(row=0, column=0, columnspan=7, sticky=tk.W, padx=14, pady=(12, 8))

        self._muted_label(form, text="Device Name").grid(row=1, column=0, sticky=tk.W, padx=(14, 8), pady=(0, 12))
        ttk.Entry(form, textvariable=self.device_name_var, style="Light.TEntry").grid(
            row=1, column=1, sticky=tk.EW, padx=(0, 12), pady=(0, 12)
        )
        self._muted_label(form, text="IP Address / Host").grid(row=1, column=2, sticky=tk.W, padx=(0, 8), pady=(0, 12))
        ttk.Entry(form, textvariable=self.device_address_var, style="Light.TEntry").grid(
            row=1, column=3, sticky=tk.EW, padx=(0, 12), pady=(0, 12)
        )
        self._muted_label(form, text="Device Type").grid(row=1, column=4, sticky=tk.W, padx=(0, 8), pady=(0, 12))
        ttk.Combobox(
            form,
            textvariable=self.device_type_var,
            values=("Router", "Server", "Printer", "Camera", "PC", "Other"),
            state="readonly",
            width=12,
            style="Light.TCombobox",
        ).grid(row=1, column=5, sticky=tk.EW, padx=(0, 12), pady=(0, 12))
        self._tool_button(form, "Add Device", self.add_device, "Accent.TButton").grid(
            row=1, column=6, sticky=tk.EW, padx=(0, 14), pady=(0, 12)
        )

        table_card = self._card(page)
        table_card.grid(row=2, column=0, sticky=tk.NSEW)
        page.rowconfigure(2, weight=1)
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(2, weight=1)

        toolbar = tk.Frame(table_card, bg=self.colors["card"])
        toolbar.grid(row=0, column=0, sticky=tk.EW, padx=14, pady=(12, 4))
        toolbar.columnconfigure(0, weight=1)
        self._section_title(toolbar, "Device List").grid(row=0, column=0, sticky=tk.W)
        self._tool_button(toolbar, "Remove Selected Device", self.remove_selected_device).grid(
            row=0, column=1, sticky=tk.E, padx=(8, 0)
        )
        self._tool_button(toolbar, "Save Devices", self.save_devices).grid(row=0, column=2, sticky=tk.E, padx=(8, 0))
        self._tool_button(toolbar, "Load Devices", self.load_devices).grid(row=0, column=3, sticky=tk.E, padx=(8, 0))
        self._tool_button(toolbar, "Check Company Network", self.check_company_network, "Accent.TButton").grid(
            row=0, column=4, sticky=tk.E, padx=(8, 0)
        )

        self._muted_label(table_card, textvariable=self.last_scan_var).grid(
            row=1, column=0, sticky=tk.W, padx=14, pady=(0, 6)
        )

        table_frame = tk.Frame(table_card, bg=self.colors["card"])
        table_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=14, pady=(0, 14))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("Name", "Address", "Type", "Last Status")
        self.devices_table = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=8, style="Light.Treeview"
        )
        for column in columns:
            self.devices_table.heading(column, text=column)
            self.devices_table.column(column, width=160, anchor=tk.W)
        self.devices_table.column("Last Status", width=120, anchor=tk.W)
        self.devices_table.tag_configure("ok", background=self.colors["green_bg"], foreground="#166534")
        self.devices_table.tag_configure("down", background=self.colors["red_bg"], foreground="#991b1b")
        self.devices_table.tag_configure("unknown", background=self.colors["orange_bg"], foreground="#92400e")
        self.devices_table.grid(row=0, column=0, sticky=tk.NSEW)

        devices_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.devices_table.yview)
        devices_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.devices_table.configure(yscrollcommand=devices_scrollbar.set)

    def build_discovery_section(self):
        page = self._create_page("discovery")
        self._page_header(
            page,
            "Network Discovery",
            "Scan the local subnet (detected from your IP and subnet mask) for active devices.",
        )

        controls = self._card(page)
        controls.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        controls.columnconfigure(2, weight=1)
        self._section_title(controls, "Discovery Controls").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=14, pady=(12, 8)
        )
        self.discover_button = self._tool_button(
            controls, "Discover Network Devices", self.discover_network_devices, "Accent.TButton"
        )
        self.discover_button.grid(row=1, column=0, sticky=tk.W, padx=(14, 8), pady=(0, 14))
        self.stop_discovery_button = self._tool_button(controls, "Stop Discovery", self.stop_discovery, "Danger.TButton")
        self.stop_discovery_button.grid(row=1, column=1, sticky=tk.W, padx=(0, 14), pady=(0, 14))
        self.stop_discovery_button.configure(state=tk.DISABLED)
        self._muted_label(controls, textvariable=self.discovery_progress_var).grid(
            row=1, column=2, sticky=tk.E, padx=(0, 14), pady=(0, 14)
        )

        summary = tk.Frame(page, bg=self.colors["bg"])
        summary.grid(row=2, column=0, sticky=tk.EW, pady=(0, 12))
        for column in range(3):
            summary.columnconfigure(column, weight=1, uniform="disc_cards")
        self._stat_card(summary, "Devices Found", self.discovery_found_var, self.colors["blue"], 0)
        self._stat_card(summary, "Known Devices", self.discovery_known_var, self.colors["green"], 1)
        self._stat_card(summary, "Unknown Devices", self.discovery_unknown_var, self.colors["orange"], 2, last=True)

        info = self._card(page)
        info.grid(row=3, column=0, sticky=tk.EW)
        info.columnconfigure(0, weight=1)
        self._section_title(info, "Last Discovery").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 4))
        self._tk_label(info, textvariable=self.last_discovery_summary_var).grid(
            row=1, column=0, sticky=tk.W, padx=14, pady=(0, 4)
        )
        self._muted_label(
            info,
            text="Devices are matched against your saved company device list. "
            "Detailed results, including MAC addresses, appear in the Results Console below.",
        ).grid(row=2, column=0, sticky=tk.W, padx=14, pady=(0, 14))

    def build_internet_quality_section(self):
        page = self._create_page("quality")
        header = self._page_header(
            page, "Internet Quality", "Measure packet loss, latency, jitter, DNS response time, and speed."
        )
        self._tool_button(header, "Internet Quality Test", self.internet_quality_test, "Accent.TButton").grid(
            row=0, column=1, rowspan=2, sticky=tk.E
        )

        metrics = self._card(page)
        metrics.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        metrics.columnconfigure(0, weight=1)
        self._section_title(metrics, "Latest Results").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 8))

        tiles = tk.Frame(metrics, bg=self.colors["card"])
        tiles.grid(row=1, column=0, sticky=tk.EW, padx=14, pady=(0, 6))
        for column in range(4):
            tiles.columnconfigure(column, weight=1, uniform="iq_tiles")
        tile_specs = [
            ("Download Speed", self.iq_download_var),
            ("Upload Speed", self.iq_upload_var),
            ("Packet Loss", self.iq_packet_loss_var),
            ("Avg Ping", self.iq_avg_ping_var),
            ("Jitter", self.iq_jitter_var),
            ("DNS Response Time", self.iq_dns_var),
            ("Score", self.iq_score_var),
            ("Status", self.iq_status_var),
        ]
        for index, (title, variable) in enumerate(tile_specs):
            row, column = divmod(index, 4)
            value_label = self._metric_tile(tiles, title, variable, row, column, last_in_row=column == 3)
            if title == "Status":
                self.iq_status_value_label = value_label
            elif title == "Score":
                value_label.configure(fg=self.colors["blue"])

        body = tk.Frame(page, bg=self.colors["bg"])
        body.grid(row=2, column=0, sticky=tk.NSEW)
        page.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        diagnosis_card = self._card(body)
        diagnosis_card.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        diagnosis_card.columnconfigure(0, weight=1)
        diagnosis_card.rowconfigure(1, weight=1)
        self._section_title(diagnosis_card, "Smart Diagnosis").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 6))
        self.diagnosis_text = tk.Text(
            diagnosis_card,
            wrap=tk.WORD,
            height=6,
            bg=self.colors["tile"],
            fg=self.colors["text"],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=8,
            state=tk.DISABLED,
        )
        self.diagnosis_text.grid(row=1, column=0, sticky=tk.NSEW, padx=14, pady=(0, 14))

        actions_card = self._card(body)
        actions_card.grid(row=0, column=1, sticky=tk.NSEW)
        actions_card.columnconfigure(0, weight=1)
        actions_card.rowconfigure(1, weight=1)
        self._section_title(actions_card, "Recommended Actions").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 6))
        self.actions_text = tk.Text(
            actions_card,
            wrap=tk.WORD,
            height=6,
            bg=self.colors["tile"],
            fg=self.colors["text"],
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=8,
            state=tk.DISABLED,
        )
        self.actions_text.grid(row=1, column=0, sticky=tk.NSEW, padx=14, pady=(0, 14))

        self._set_text_widget(self.diagnosis_text, ["Run the Internet Quality Test to see the smart diagnosis here."])
        self._set_text_widget(self.actions_text, ["Run the Internet Quality Test to see recommended actions here."])

    def build_logs_section(self):
        page = self._create_page("logs")
        self._page_header(page, "Logs / Reports", "Automatic daily logs and manual report exports.")

        info = self._card(page)
        info.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))
        info.columnconfigure(0, weight=1)
        self._section_title(info, "Automatic Daily Logs").grid(row=0, column=0, sticky=tk.W, padx=14, pady=(12, 4))
        self._muted_label(
            info, text="Every tool result is appended automatically to a daily log file (one file per day)."
        ).grid(row=1, column=0, sticky=tk.W, padx=14, pady=(0, 4))
        self._muted_label(info, text=f"Logs folder: {self.logs_folder}").grid(
            row=2, column=0, sticky=tk.W, padx=14, pady=(0, 4)
        )
        self._muted_label(info, text=f"Devices file: {self.devices_file}").grid(
            row=3, column=0, sticky=tk.W, padx=14, pady=(0, 12)
        )

        buttons = self._card(page)
        buttons.grid(row=2, column=0, sticky=tk.EW)
        self._section_title(buttons, "Actions").grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=14, pady=(12, 8))
        self._tool_button(buttons, "Open Logs Folder", self.open_logs_folder, "Accent.TButton").grid(
            row=1, column=0, sticky=tk.W, padx=(14, 8), pady=(0, 14)
        )
        self._tool_button(buttons, "Save Report", self.save_report).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 8), pady=(0, 14)
        )
        self._tool_button(buttons, "Clear Output", self.clear_output).grid(
            row=1, column=2, sticky=tk.W, padx=(0, 14), pady=(0, 14)
        )

    def build_results_section(self, parent):
        results = self._card(parent)
        results.grid(row=1, column=0, sticky=tk.NSEW, pady=(12, 0))
        results.rowconfigure(1, weight=1)
        results.columnconfigure(0, weight=1)

        results_header = tk.Frame(results, bg=self.colors["card"])
        results_header.grid(row=0, column=0, sticky=tk.EW, padx=14, pady=(12, 8))
        results_header.columnconfigure(1, weight=1)
        self._section_title(results_header, "Results Console").grid(row=0, column=0, sticky=tk.W)
        self._muted_label(results_header, textvariable=self.status_var).grid(
            row=0, column=1, sticky=tk.W, padx=(14, 0)
        )
        self._tool_button(results_header, "Clear Output", self.clear_output).grid(row=0, column=2, sticky=tk.E, padx=(8, 0))
        self._tool_button(results_header, "Save Report", self.save_report).grid(row=0, column=3, sticky=tk.E, padx=(8, 0))

        output_shell = tk.Frame(results, bg=self.colors["card"])
        output_shell.grid(row=1, column=0, sticky=tk.NSEW, padx=14, pady=(0, 14))
        output_shell.rowconfigure(0, weight=1)
        output_shell.columnconfigure(0, weight=1)
        self.output = scrolledtext.ScrolledText(
            output_shell,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 10),
            bg=self.colors["console_bg"],
            fg=self.colors["console_fg"],
            insertbackground="#f3f4f6",
            selectbackground="#2563eb",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.output.grid(row=0, column=0, sticky=tk.NSEW)

    # ------------------------------------------------------------------
    # UI state updates
    # ------------------------------------------------------------------
    def _update_status_indicator(self, *_args):
        if not hasattr(self, "status_dot_label"):
            return
        running = self.status_var.get().startswith("Running")
        self.status_dot_label.configure(fg=self.colors["blue"] if running else self.colors["green"])

    def status_color(self, status):
        if status in ("HEALTHY", "EXCELLENT", "GOOD", "OK"):
            return self.colors["green"]
        if status in ("WARNING", "Not checked", "UNKNOWN"):
            return self.colors["orange"]
        if status in ("CRITICAL", "BAD", "DOWN"):
            return self.colors["red"]
        return self.colors["muted"]

    def refresh_dashboard_stats(self):
        if not hasattr(self, "devices_table"):
            return

        devices = self.get_devices()
        total_count = len(devices)
        ok_count = sum(1 for device in devices if device.get("last_status") == "OK")
        down_count = sum(1 for device in devices if device.get("last_status") == "DOWN")
        unknown_count = max(total_count - ok_count - down_count, 0)

        self.total_devices_var.set(str(total_count))
        self.ok_devices_var.set(str(ok_count))
        self.down_devices_var.set(str(down_count))
        self.unknown_devices_var.set(str(unknown_count))
        self.active_devices_var.set(f"{ok_count} / {total_count}")

    def update_internet_quality_details(self, report_lines):
        field_targets = {
            "Download Speed:": self.iq_download_var,
            "Upload Speed:": self.iq_upload_var,
            "Packet Loss:": self.iq_packet_loss_var,
            "Avg Ping:": self.iq_avg_ping_var,
            "Jitter:": self.iq_jitter_var,
            "DNS Response Time:": self.iq_dns_var,
            "Internet Quality Score:": self.iq_score_var,
            "Status:": self.iq_status_var,
        }
        diagnosis_lines = []
        action_lines = []
        current_section = None

        for line in report_lines:
            stripped = line.strip()
            if stripped == "Smart Diagnosis:":
                current_section = "diagnosis"
                continue
            if stripped == "Recommended Actions:":
                current_section = "actions"
                continue
            if current_section and stripped.startswith("- "):
                if current_section == "diagnosis":
                    diagnosis_lines.append(stripped[2:])
                else:
                    action_lines.append(stripped[2:])
                continue
            for prefix, variable in field_targets.items():
                if stripped.startswith(prefix):
                    variable.set(stripped[len(prefix):].strip() or "Not available")
                    break

        if hasattr(self, "iq_status_value_label"):
            self.iq_status_value_label.configure(fg=self.status_color(self.iq_status_var.get()))
        if diagnosis_lines and hasattr(self, "diagnosis_text"):
            self._set_text_widget(self.diagnosis_text, diagnosis_lines)
        if action_lines and hasattr(self, "actions_text"):
            self._set_text_widget(self.actions_text, action_lines)

    def update_internet_quality_summary(self, report_lines):
        self.update_internet_quality_details(report_lines)

        score_text = None
        status_text = None

        for line in report_lines:
            if line.startswith("Internet Quality Score:"):
                score_text = line.split(":", 1)[1].strip().split("/", 1)[0].strip()
            elif line.startswith("Status:"):
                status_text = line.split(":", 1)[1].strip()

        if not score_text:
            return

        try:
            score_value = float(score_text)
            display_score = f"{score_value:.0f}%"
        except ValueError:
            display_score = score_text

        if status_text:
            self.internet_quality_var.set(f"Internet Quality: {display_score} - {status_text}")
            color = self.status_color(status_text)
        else:
            self.internet_quality_var.set(f"Internet Quality: {display_score}")
            color = self.colors["blue"]

        self.internet_quality_score_var.set(display_score)
        if hasattr(self, "internet_quality_top_label"):
            self.internet_quality_top_label.configure(fg=color)
        if hasattr(self, "internet_quality_card_value"):
            self.internet_quality_card_value.configure(fg=color)

    def update_discovery_summary(self, found_count, known_count, unknown_count):
        self.discovery_found_var.set(str(found_count))
        self.discovery_known_var.set(str(known_count))
        self.discovery_unknown_var.set(str(unknown_count))
        self.last_discovery_summary_var.set(
            f"Last discovery: {found_count} device(s) found - {known_count} known, {unknown_count} unknown "
            f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        )

    # ------------------------------------------------------------------
    # Background task plumbing, logging, and reports
    # ------------------------------------------------------------------
    def run_in_background(self, title, task):
        self.status_var.set(f"Running: {title}")
        self.write_section(title)

        def worker():
            try:
                task()
            except Exception as error:
                self.write_line(f"ERROR: {error}")
            finally:
                self.after(0, self.status_var.set, "Ready")

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
        logger_utils.write_daily_log(self.logs_folder, text)

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

    # ------------------------------------------------------------------
    # Company devices
    # ------------------------------------------------------------------
    def add_device(self):
        name = self.device_name_var.get().strip()
        address = self.device_address_var.get().strip()
        device_type = self.device_type_var.get().strip() or "Other"

        if not name:
            messagebox.showinfo("Add Device", "Please enter a device name.")
            return
        if not address:
            messagebox.showinfo("Add Device", "Please enter an IP address or host.")
            return

        self.devices_table.insert("", END, values=(name, address, device_type, "Not checked"), tags=("unknown",))
        self.device_name_var.set("")
        self.device_address_var.set("")
        self.device_type_var.set("Router")
        self.status_var.set(f"Added device: {name}")
        self.refresh_dashboard_stats()

    def remove_selected_device(self):
        selected_items = self.devices_table.selection()
        if not selected_items:
            messagebox.showinfo("Remove Selected Device", "Please select a device to remove.")
            return

        for item in selected_items:
            self.devices_table.delete(item)
        self.status_var.set("Selected device removed")
        self.refresh_dashboard_stats()

    def get_devices(self):
        devices = []
        for item in self.devices_table.get_children():
            name, address, device_type, last_status = self.devices_table.item(item, "values")
            devices.append(
                {
                    "name": name,
                    "address": address,
                    "type": device_type,
                    "last_status": last_status,
                }
            )
        return devices

    def save_devices(self):
        devices = self.get_devices()
        try:
            devices_manager.save_devices(self.devices_file, devices)
        except OSError as error:
            messagebox.showerror("Save Devices", f"Could not save devices.json.\n\n{error}")
            return
        self.status_var.set(f"Saved {len(devices)} device(s)")
        self.write_line(f"Saved {len(devices)} company device(s) to {self.devices_file.name}.")

    def load_devices(self, show_message=True):
        if not self.devices_file.exists():
            if show_message:
                messagebox.showinfo("Load Devices", "No devices.json file was found yet.")
            return

        try:
            devices = devices_manager.load_devices(self.devices_file)
        except (OSError, ValueError) as error:
            messagebox.showerror("Load Devices", f"Could not load devices.json.\n\n{error}")
            return

        self.devices_table.delete(*self.devices_table.get_children())
        for device in devices:
            last_status = device.get("last_status", "Not checked")
            self.devices_table.insert(
                "",
                END,
                values=(
                    device.get("name", ""),
                    device.get("address", ""),
                    device.get("type", "Other"),
                    last_status,
                ),
                tags=(self.status_to_tag(last_status),),
            )

        self.status_var.set(f"Loaded {len(devices)} device(s)")
        self.refresh_dashboard_stats()
        if show_message:
            self.write_line(f"Loaded {len(devices)} company device(s) from {self.devices_file.name}.")

    def status_to_tag(self, status):
        if status == "OK":
            return "ok"
        if status == "DOWN":
            return "down"
        return "unknown"

    def set_device_status(self, item, status):
        current_values = list(self.devices_table.item(item, "values"))
        if len(current_values) == 4:
            current_values[3] = status
            self.devices_table.item(item, values=current_values, tags=(self.status_to_tag(status),))
            self.refresh_dashboard_stats()

    def format_health_score(self, health_score):
        if health_score.is_integer():
            return f"{health_score:.0f}%"
        return f"{health_score:.1f}%"

    def get_health_status(self, health_score):
        if health_score == 100:
            return "HEALTHY"
        if health_score >= 50:
            return "WARNING"
        return "CRITICAL"

    def update_network_health_label(self, health_score, health_status):
        health_score_text = self.format_health_score(health_score)
        color = self.status_color(health_status)
        self.network_health_var.set(f"Network Health: {health_score_text} - {health_status}")
        self.network_health_score_var.set(health_score_text)
        self.network_health_status_var.set(health_status)

        if hasattr(self, "network_health_top_label"):
            self.network_health_top_label.configure(fg=color)
        if hasattr(self, "network_health_panel_label"):
            self.network_health_panel_label.configure(fg=color)
        if hasattr(self, "network_health_card_value"):
            self.network_health_card_value.configure(fg=color)

    def ping_device_once(self, address):
        result, error = network_tools.run_command(["ping", "-n", "1", "-w", "1000", address])
        if error:
            self.write_line("ERROR: The Windows ping command was not found.")
            return False
        return result.returncode == 0

    # ------------------------------------------------------------------
    # Network discovery
    # ------------------------------------------------------------------
    def update_discovery_progress(self, current, total):
        self.discovery_progress_var.set(f"Discovering devices... {current}/{total}")

    def finish_discovery_progress(self, found_count):
        self.discovery_progress_var.set(f"Discovery finished: {found_count} found")

    def set_discovery_controls(self, running):
        if running:
            self.discover_button.configure(state=tk.DISABLED)
            self.stop_discovery_button.configure(state=tk.NORMAL)
            self.status_var.set("Running: Discover Network Devices")
        else:
            self.discover_button.configure(state=tk.NORMAL)
            self.stop_discovery_button.configure(state=tk.DISABLED)
            self.status_var.set("Ready")

    def stop_discovery(self):
        if not self.discovery_running:
            self.write_line("No discovery is currently running.")
            return

        self.discovery_cancel_event.set()
        self.discovery_progress_var.set("Discovery stop requested...")
        self.write_line("Discovery stop requested...")

    def discover_network_devices(self):
        if self.discovery_running:
            messagebox.showinfo("Discover Network Devices", "Discovery is already running.")
            return

        adapter = discovery.get_active_network_details()
        if adapter is None:
            messagebox.showerror(
                "Discover Network Devices",
                "Could not detect local IP/subnet mask for discovery.",
            )
            return

        network, scan_addresses, error_message = discovery.calculate_scan_plan(adapter)
        local_ip = adapter["ip"]
        subnet_mask = adapter["subnet_mask"]
        gateway = adapter["gateway"]

        if error_message:
            self.write_section("Discover Network Devices")
            self.write_line(f"Local IP: {local_ip}")
            self.write_line(f"Subnet Mask: {subnet_mask}")
            self.write_line(f"Default Gateway: {gateway}")
            if network:
                self.write_line(f"Network: {network}")
            self.write_line(error_message)
            return

        known_addresses = discovery.get_known_device_addresses(self.get_devices())
        self.discovery_running = True
        self.discovery_cancel_event.clear()
        self.set_discovery_controls(running=True)

        def task():
            discovered_devices = []
            known_devices = []
            unknown_devices = []
            total_ips = len(scan_addresses)
            completed = 0
            stopped = False

            try:
                self.write_section("Discover Network Devices")
                self.write_line(f"Local IP: {local_ip}")
                self.write_line(f"Subnet Mask: {subnet_mask}")
                self.write_line(f"Default Gateway: {gateway}")
                self.write_line(f"Network: {network}")
                self.write_line(f"Scan range: {scan_addresses[0]} - {scan_addresses[-1]}")
                self.write_line("Starting authorized local network discovery.")

                with ThreadPoolExecutor(max_workers=30) as executor:
                    futures = [
                        executor.submit(
                            discovery.discover_single_address,
                            address,
                            known_addresses,
                            self.discovery_cancel_event,
                        )
                        for address in scan_addresses
                    ]

                    for future in as_completed(futures):
                        completed += 1
                        self.after(0, self.update_discovery_progress, completed, total_ips)

                        if self.discovery_cancel_event.is_set():
                            stopped = True
                            for pending_future in futures:
                                pending_future.cancel()
                            break

                        result = future.result()
                        if result is None:
                            continue

                        address, mac_address, status = result
                        discovered_devices.append((address, mac_address, status))

                        if status == "KNOWN":
                            known_devices.append((address, mac_address))
                        else:
                            unknown_devices.append((address, mac_address))

                        self.write_line(f"Discovered {status} device: {address} | MAC: {mac_address}")

                self.write_line("")
                self.write_line("Network Discovery Summary")
                self.write_line("-------------------------")
                self.write_line(f"Total scanned: {completed}")
                self.write_line(f"Total IPs in subnet: {total_ips}")
                self.write_line(f"Devices found: {len(discovered_devices)}")
                self.write_line(f"Known devices: {len(known_devices)}")
                self.write_line(f"Unknown devices: {len(unknown_devices)}")
                self.write_line("")
                self.write_line("Unknown devices:")
                if unknown_devices:
                    for address, mac_address in unknown_devices:
                        self.write_line(f"Unknown device found: {address} | MAC: {mac_address}")
                else:
                    self.write_line("None")

            except Exception as error:
                self.write_line(f"ERROR: Discovery failed. Details: {error}")
            finally:
                stopped = stopped or self.discovery_cancel_event.is_set()
                self.discovery_running = False
                self.after(0, self.set_discovery_controls, False)
                self.after(0, self.last_scan_var.set, f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.after(
                    0,
                    self.update_discovery_summary,
                    len(discovered_devices),
                    len(known_devices),
                    len(unknown_devices),
                )

                if stopped:
                    self.after(0, self.discovery_progress_var.set, f"Discovery stopped: {completed}/{total_ips}")
                    self.write_line("Discovery stopped.")
                else:
                    self.after(0, self.finish_discovery_progress, len(discovered_devices))
                    self.write_line("Discovery finished.")

        threading.Thread(target=task, daemon=True).start()

    def check_company_network(self):
        items = list(self.devices_table.get_children())
        if not items:
            messagebox.showinfo("Check Company Network", "Please add or load at least one company device.")
            return

        device_rows = []
        for item in items:
            name, address, device_type, last_status = self.devices_table.item(item, "values")
            device_rows.append((item, name, address, device_type, last_status))

        def task():
            ok_devices = []
            down_devices = []

            self.write_line(f"Checking {len(device_rows)} company device(s)...")
            for item, name, address, device_type, _last_status in device_rows:
                self.write_line(f"Pinging {name} ({device_type}) at {address}...")
                status = "OK" if self.ping_device_once(address) else "DOWN"
                self.after(0, self.set_device_status, item, status)
                self.write_line(f"{name} [{address}] status: {status}")

                if status == "OK":
                    ok_devices.append((name, address, device_type))
                else:
                    down_devices.append((name, address, device_type))

            total_devices = len(device_rows)
            ok_count = len(ok_devices)
            down_count = len(down_devices)
            health_score = (ok_count / total_devices) * 100
            health_status = self.get_health_status(health_score)
            last_check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.after(0, self.update_network_health_label, health_score, health_status)
            self.after(0, self.last_scan_var.set, f"Last scan: {last_check_time}")
            self.after(0, self.refresh_dashboard_stats)

            self.write_line("")
            self.write_line("Company Network Summary")
            self.write_line("-----------------------")
            self.write_line(f"Total devices: {total_devices}")
            self.write_line(f"OK devices: {ok_count}")
            self.write_line(f"DOWN devices: {down_count}")
            self.write_line(f"Health Score: {self.format_health_score(health_score)}")
            self.write_line(f"Status: {health_status}")
            self.write_line(f"Last check time: {last_check_time}")
            self.write_line("")
            self.write_line("DOWN devices:")
            if down_devices:
                for name, address, device_type in down_devices:
                    self.write_line(f"- {name} ({device_type}) at {address}")
            else:
                self.write_line("None")
            self.write_line("Company network check finished.")

        self.run_in_background("Check Company Network", task)

    # ------------------------------------------------------------------
    # Basic network tools
    # ------------------------------------------------------------------
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
        result, error = network_tools.run_command(command)
        if error:
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
            self.write_line(network_tools.check_tcp_port(host, port))

        self.run_in_background("TCP Port Check", task)

    def dns_lookup(self):
        host = self.get_host()
        if not host:
            return

        def task():
            self.write_line(f"Resolving {host}...")
            unique_ips, error = network_tools.resolve_host_addresses(host)
            if error:
                self.write_line(f"ERROR: Could not resolve host name: {host}")
                return
            for ip_address in unique_ips:
                self.write_line(f"{host} resolves to {ip_address}")

        self.run_in_background("DNS Lookup", task)

    def local_ip(self):
        def task():
            self.write_line(f"Computer name: {socket.gethostname()}")
            local_ip, error = network_tools.get_local_ip()
            if error:
                self.write_line("ERROR: Could not find the local IP address.")
            else:
                self.write_line(f"Local IP address: {local_ip}")

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
            public_ip, error = network_tools.get_public_ip()
            if error:
                self.write_line(f"ERROR: Could not look up public IP address. Details: {error}")
            else:
                self.write_line(f"Public IP address: {public_ip}")

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

        ports = network_tools.parse_ports(self.scan_ports_var.get())
        if not ports:
            self.write_line("Please enter ports like 80,443,3389 or ranges like 20-25.")
            return

        def task():
            self.write_line(f"Scanning {len(ports)} TCP port(s) on {host}...")
            for port in ports:
                self.write_line(network_tools.check_tcp_port(host, port))

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
                self.write_line(network_tools.check_tcp_port(host, port))

        self.run_in_background("Full Host Check", task)

    def internet_troubleshooter(self):
        def task():
            self.write_line("Running basic internet troubleshooting checks.")

            self.write_line("")
            self.write_line("[Local IP]")
            local_ip, error = network_tools.get_local_ip()
            if error:
                self.write_line("Could not confirm local IP using an outbound test socket.")
            else:
                self.write_line(f"Local IP address: {local_ip}")

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
            public_ip, public_error = network_tools.get_public_ip()
            if public_error:
                self.write_line(f"Public IP lookup failed: {public_error}")
            else:
                self.write_line(f"Public IP address: {public_ip}")

            self.write_line("")
            self.write_line("Troubleshooter finished.")

        self.run_in_background("Internet Troubleshooter", task)

    def internet_quality_test(self):
        def task():
            report_lines = internet_quality.run_internet_quality_test(progress_callback=self.write_line)
            for line in report_lines:
                self.write_line(line)
            self.after(0, self.update_internet_quality_summary, report_lines)

        self.run_in_background("Internet Quality Test", task)


if __name__ == "__main__":
    app = SmartInternetTroubleshooter()
    app.mainloop()
