package com.iotids.networkengine.capture;

import com.iotids.networkengine.config.CaptureConfig;
import com.iotids.networkengine.logging.NetworkLogger;
import org.pcap4j.core.BpfProgram;
import org.pcap4j.core.NotOpenException;
import org.pcap4j.core.PacketListener;
import org.pcap4j.core.PcapHandle;
import org.pcap4j.core.PcapNetworkInterface;
import org.pcap4j.core.PcapNativeException;
import org.pcap4j.packet.Packet;

public class PacketCapture implements Runnable {
    private static final NetworkLogger logger = NetworkLogger.getLogger(PacketCapture.class);
    private final CaptureConfig config;
    private final com.iotids.networkengine.capture.PacketListener listener;
    private volatile boolean running = false;
    private PcapHandle handle;

    public PacketCapture(CaptureConfig config, com.iotids.networkengine.capture.PacketListener listener) {
        this.config = config;
        this.listener = listener;
    }

    public void stop() {
        running = false;
        if (handle != null && handle.isOpen()) {
            try {
                handle.breakLoop();
            } catch (NotOpenException e) {
                logger.warn("Handle already closed");
            }
        }
    }

    @Override
    public void run() {
        PcapNetworkInterface nif = InterfaceManager.getNetworkInterface(config.getNetworkInterfaceName());
        if (nif == null) {
            logger.error("No suitable network interface found. Capture stopped.");
            return;
        }

        try {
            PcapNetworkInterface.PromiscuousMode mode = config.isPromiscuousMode() ? 
                    PcapNetworkInterface.PromiscuousMode.PROMISCUOUS : 
                    PcapNetworkInterface.PromiscuousMode.NONPROMISCUOUS;
                    
            handle = nif.openLive(config.getSnapshotLength(), mode, config.getReadTimeoutMs());
            logger.info("Started packet capture on " + nif.getName());
            
            running = true;
            PacketListener pcapListener = new PacketListener() {
                @Override
                public void gotPacket(Packet packet) {
                    listener.onPacket(packet);
                }
            };

            while (running) {
                try {
                    handle.loop(10, pcapListener);
                } catch (InterruptedException e) {
                    running = false;
                    Thread.currentThread().interrupt();
                }
            }
        } catch (PcapNativeException | NotOpenException e) {
            logger.error("Capture error: " + e.getMessage(), e);
        } finally {
            if (handle != null && handle.isOpen()) {
                handle.close();
                logger.info("Capture handle closed");
            }
        }
    }
}
