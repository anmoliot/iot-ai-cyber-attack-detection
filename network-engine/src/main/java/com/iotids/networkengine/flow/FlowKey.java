package com.iotids.networkengine.flow;

import java.util.Objects;

public class FlowKey {
    private final String srcIp;
    private final String dstIp;
    private final String protocol;

    public FlowKey(String srcIp, String dstIp, String protocol) {
        this.srcIp = srcIp;
        this.dstIp = dstIp;
        this.protocol = protocol;
    }

    public String getSrcIp() { return srcIp; }
    public String getDstIp() { return dstIp; }
    public String getProtocol() { return protocol; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        FlowKey flowKey = (FlowKey) o;
        return Objects.equals(srcIp, flowKey.srcIp) &&
               Objects.equals(dstIp, flowKey.dstIp) &&
               Objects.equals(protocol, flowKey.protocol);
    }

    @Override
    public int hashCode() {
        return Objects.hash(srcIp, dstIp, protocol);
    }

    @Override
    public String toString() {
        return srcIp + "->" + dstIp + ":" + protocol;
    }
}
