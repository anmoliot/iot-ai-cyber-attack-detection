package com.iotids.networkengine.flow;

import com.iotids.networkengine.packet.ParsedPacket;
import com.iotids.networkengine.logging.NetworkLogger;

public class FlowManager {
    private static final NetworkLogger logger = NetworkLogger.getLogger(FlowManager.class);
    private final FlowCache flowCache;

    public FlowManager(FlowCache flowCache) {
        this.flowCache = flowCache;
    }

    public void processPacket(ParsedPacket packet) {
        if (packet == null) return;
        
        FlowKey key = new FlowKey(packet.getSrcIp(), packet.getDstIp(), packet.getProtocol().name());
        FlowData flow = flowCache.getOrCreate(key, packet.getTimestamp());
        
        flow.addPacket(packet.getLength(), packet.getTimestamp());
    }
}
