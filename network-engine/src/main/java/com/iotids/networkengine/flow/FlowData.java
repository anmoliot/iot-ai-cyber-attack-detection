package com.iotids.networkengine.flow;

public class FlowData {
    private final FlowKey key;
    private int packetCount;
    private int byteCount;
    private final long startTime;
    private long lastSeenTime;

    public FlowData(FlowKey key, long timestamp) {
        this.key = key;
        this.startTime = timestamp;
        this.lastSeenTime = timestamp;
        this.packetCount = 0;
        this.byteCount = 0;
    }

    public synchronized void addPacket(int bytes, long timestamp) {
        this.packetCount++;
        this.byteCount += bytes;
        this.lastSeenTime = Math.max(this.lastSeenTime, timestamp);
    }

    public FlowKey getKey() { return key; }
    public synchronized int getPacketCount() { return packetCount; }
    public synchronized int getByteCount() { return byteCount; }
    public long getStartTime() { return startTime; }
    public synchronized long getLastSeenTime() { return lastSeenTime; }
    
    public synchronized long getDurationMillis() {
        return Math.max(0, lastSeenTime - startTime);
    }
}
