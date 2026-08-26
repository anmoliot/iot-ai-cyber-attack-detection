package com.iotids.networkengine.flow;

public class FlowData {
    private FlowKey key;
    private int packetCount;
    private int byteCount;
    private long durationMillis;

    public FlowData(FlowKey key) {
        this.key = key;
    }

    public FlowKey getKey() {
        return key;
    }

    public int getPacketCount() {
        return packetCount;
    }

    public int getByteCount() {
        return byteCount;
    }

    public long getDurationMillis() {
        return durationMillis;
    }
}
