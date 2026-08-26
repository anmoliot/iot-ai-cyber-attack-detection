package com.iotids.networkengine.config;

public class CaptureConfig {
    private String networkInterfaceName = "";
    private int snapshotLength = 65536;
    private int readTimeoutMs = 10;
    private boolean promiscuousMode = true;

    public String getNetworkInterfaceName() { return networkInterfaceName; }
    public void setNetworkInterfaceName(String networkInterfaceName) { this.networkInterfaceName = networkInterfaceName; }

    public int getSnapshotLength() { return snapshotLength; }
    public void setSnapshotLength(int snapshotLength) { this.snapshotLength = snapshotLength; }

    public int getReadTimeoutMs() { return readTimeoutMs; }
    public void setReadTimeoutMs(int readTimeoutMs) { this.readTimeoutMs = readTimeoutMs; }

    public boolean isPromiscuousMode() { return promiscuousMode; }
    public void setPromiscuousMode(boolean promiscuousMode) { this.promiscuousMode = promiscuousMode; }
}
