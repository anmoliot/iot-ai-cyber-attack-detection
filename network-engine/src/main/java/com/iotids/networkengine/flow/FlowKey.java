package com.iotids.networkengine.flow;

public class FlowKey {
    private String srcIp;
    private String dstIp;
    private String protocol;

    public String getSrcIp() { return srcIp; }
    public String getDstIp() { return dstIp; }
    public String getProtocol() { return protocol; }
}
