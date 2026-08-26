package com.iotids.networkengine.feature;

public class FeatureVector {
    private final int packetCount;
    private final int byteCount;
    private final long durationMs;
    private final String srcIp;
    private final String dstIp;
    private final String protocol;

    public FeatureVector(int packetCount, int byteCount, long durationMs, String srcIp, String dstIp, String protocol) {
        this.packetCount = packetCount;
        this.byteCount = byteCount;
        this.durationMs = durationMs;
        this.srcIp = srcIp;
        this.dstIp = dstIp;
        this.protocol = protocol;
    }

    public int getPacketCount() { return packetCount; }
    public int getByteCount() { return byteCount; }
    public long getDurationMs() { return durationMs; }
    public String getSrcIp() { return srcIp; }
    public String getDstIp() { return dstIp; }
    public String getProtocol() { return protocol; }
}
