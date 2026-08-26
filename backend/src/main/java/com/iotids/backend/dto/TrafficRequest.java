package com.iotids.backend.dto;

public class TrafficRequest {
    private String sourceIp;
    private String destinationIp;
    private String protocol;
    private int bytes;
    private int packets;

    // Getters and Setters
    public String getSourceIp() { return sourceIp; }
    public void setSourceIp(String sourceIp) { this.sourceIp = sourceIp; }

    public String getDestinationIp() { return destinationIp; }
    public void setDestinationIp(String destinationIp) { this.destinationIp = destinationIp; }

    public String getProtocol() { return protocol; }
    public void setProtocol(String protocol) { this.protocol = protocol; }

    public int getBytes() { return bytes; }
    public void setBytes(int bytes) { this.bytes = bytes; }

    public int getPackets() { return packets; }
    public void setPackets(int packets) { this.packets = packets; }
}
