package com.iotids.networkengine.packet;

public class ParsedPacket {
    private final String srcIp;
    private final String dstIp;
    private final ProtocolType protocol;
    private final int length;
    private final long timestamp;

    public ParsedPacket(String srcIp, String dstIp, ProtocolType protocol, int length, long timestamp) {
        this.srcIp = srcIp;
        this.dstIp = dstIp;
        this.protocol = protocol;
        this.length = length;
        this.timestamp = timestamp;
    }

    public String getSrcIp() { return srcIp; }
    public String getDstIp() { return dstIp; }
    public ProtocolType getProtocol() { return protocol; }
    public int getLength() { return length; }
    public long getTimestamp() { return timestamp; }
}
