package com.iotids.networkengine.response;

import com.iotids.networkengine.logging.NetworkLogger;

import java.io.IOException;

public class FirewallService {
    private static final NetworkLogger logger = NetworkLogger.getLogger(FirewallService.class);

    public void blockIp(String ipAddress) {
        if (ipAddress == null || ipAddress.isEmpty()) return;

        logger.info("Executing firewall block for IP: " + ipAddress);
        
        try {
            // Using PowerShell to block the IP in Windows Firewall
            String command = String.format("powershell -Command \"New-NetFirewallRule -DisplayName 'IoT-IDS-Block-%s' -Direction Inbound -Action Block -RemoteAddress %s\"", ipAddress, ipAddress);
            Process process = Runtime.getRuntime().exec(command);
            
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                logger.info("Successfully blocked IP " + ipAddress + " in Windows Firewall.");
            } else {
                logger.error("Failed to block IP " + ipAddress + ". Process exited with code " + exitCode);
            }
        } catch (IOException | InterruptedException e) {
            logger.error("Error executing firewall block rule: " + e.getMessage());
            if (e instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
