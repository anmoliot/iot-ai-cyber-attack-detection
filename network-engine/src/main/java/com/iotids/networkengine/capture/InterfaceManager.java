package com.iotids.networkengine.capture;

import com.iotids.networkengine.logging.NetworkLogger;
import org.pcap4j.core.PcapNetworkInterface;
import org.pcap4j.core.Pcaps;
import java.util.List;

public class InterfaceManager {
    private static final NetworkLogger logger = NetworkLogger.getLogger(InterfaceManager.class);

    public static PcapNetworkInterface getNetworkInterface(String name) {
        try {
            if (name != null && !name.isEmpty()) {
                PcapNetworkInterface nif = Pcaps.getDevByName(name);
                if (nif != null) {
                    return nif;
                }
                logger.warn("Interface '" + name + "' not found. Searching for default.");
            }
            
            // Fallback to finding active interface
            List<PcapNetworkInterface> allDevs = Pcaps.findAllDevs();
            for (PcapNetworkInterface dev : allDevs) {
                if (dev.getAddresses() != null && !dev.getAddresses().isEmpty() && !dev.isLoopBack()) {
                    logger.info("Found active network interface: " + dev.getName() + " - " + dev.getDescription());
                    return dev;
                }
            }
        } catch (Exception e) {
            logger.error("Failed to find network interfaces: " + e.getMessage(), e);
        }
        return null;
    }
}
