package com.iotids.networkengine.response;

import com.iotids.networkengine.logging.NetworkLogger;

public class DryRunFirewallService {
    private static final NetworkLogger logger = NetworkLogger.getLogger(DryRunFirewallService.class);

    public void blockIp(String ipAddress) {
        if (ipAddress == null || ipAddress.isEmpty()) return;

        logger.info("[DRY RUN] Would execute firewall block for IP: " + ipAddress);
        logger.info("[DRY RUN] PowerShell Command: New-NetFirewallRule -DisplayName 'IoT-IDS-Block-" + ipAddress + "' -Direction Inbound -Action Block -RemoteAddress " + ipAddress);
    }
}
