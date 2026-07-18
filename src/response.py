from __future__ import annotations

import os
import platform
import subprocess


class FirewallResponse:
    def __init__(self, enabled: bool | None = None) -> None:
        if enabled is None:
            enabled = os.getenv("ENABLE_FIREWALL_BLOCK", "false").lower() == "true"
        self.enabled = enabled

    def block_ip(self, ip_address: str) -> str:
        if not self.enabled:
            return f"Dry run: would block {ip_address}"

        if platform.system().lower() != "linux":
            return "Firewall blocking is only implemented for Linux iptables in this scaffold."

        command = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
        subprocess.run(command, check=True)
        return f"Blocked {ip_address} with iptables"
