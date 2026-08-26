package com.iotids.networkengine.config;

/**
 * Configuration holder for the network engine.
 * In a real system this would load properties from a file or environment.
 */
public class NetworkConfig {
    private int captureThreadPoolSize = 2;
    private int flowThreadPoolSize = 2;

    public static NetworkConfig load() {
        // Placeholder static loader – returns default config.
        return new NetworkConfig();
    }

    public int getCaptureThreadPoolSize() {
        return captureThreadPoolSize;
    }

    public int getFlowThreadPoolSize() {
        return flowThreadPoolSize;
    }
}
