package com.iotids.networkengine.config;

public class FlowConfig {
    private long flowTimeoutMs = 60000; // 60 seconds
    private long cleanupIntervalMs = 10000; // 10 seconds

    public long getFlowTimeoutMs() { return flowTimeoutMs; }
    public void setFlowTimeoutMs(long flowTimeoutMs) { this.flowTimeoutMs = flowTimeoutMs; }

    public long getCleanupIntervalMs() { return cleanupIntervalMs; }
    public void setCleanupIntervalMs(long cleanupIntervalMs) { this.cleanupIntervalMs = cleanupIntervalMs; }
}
