package com.iotids.networkengine.orchestration;

import com.iotids.networkengine.config.ApplicationConfig;

public class NetworkOrchestrator {
    private ApplicationConfig config;

    public NetworkOrchestrator(ApplicationConfig config) {
        this.config = config;
    }

    public void start() {
        // Placeholder
        System.out.println("NetworkOrchestrator started.");
    }

    public void stop() {
        // Placeholder
        System.out.println("NetworkOrchestrator stopped.");
    }
}
