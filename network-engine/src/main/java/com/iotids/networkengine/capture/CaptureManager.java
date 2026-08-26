package com.iotids.networkengine.capture;

import com.iotids.networkengine.config.CaptureConfig;
import com.iotids.networkengine.logging.NetworkLogger;

public class CaptureManager {
    private static final NetworkLogger logger = NetworkLogger.getLogger(CaptureManager.class);
    private final CaptureConfig config;
    private final PacketListener listener;
    private PacketCapture capture;
    private Thread captureThread;

    public CaptureManager(CaptureConfig config, PacketListener listener) {
        this.config = config;
        this.listener = listener;
    }

    public void start() {
        if (captureThread != null && captureThread.isAlive()) {
            logger.warn("CaptureManager is already running");
            return;
        }
        
        logger.info("Starting CaptureManager...");
        capture = new PacketCapture(config, listener);
        captureThread = new Thread(capture, "PacketCapture-Thread");
        captureThread.start();
    }

    public void stop() {
        if (capture != null) {
            logger.info("Stopping CaptureManager...");
            capture.stop();
            try {
                if (captureThread != null) {
                    captureThread.join(2000);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
