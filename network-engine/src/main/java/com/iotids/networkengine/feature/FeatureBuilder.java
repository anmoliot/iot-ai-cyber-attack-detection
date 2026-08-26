package com.iotids.networkengine.feature;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.iotids.networkengine.flow.FlowData;
import com.iotids.networkengine.flow.FlowKey;

/**
 * Builds a JSON feature object from a FlowData instance.
 * The schema matches the ML service expectations:
 *   packet_count:int, byte_count:int, duration_ms:long,
 *   src_ip:string, dst_ip:string, protocol:string
 */
public class FeatureBuilder {
    private static final JsonNodeFactory factory = JsonNodeFactory.instance;

    public ObjectNode buildFeature(FlowData flowData) {
        FlowKey key = flowData.getKey();
        ObjectNode node = factory.objectNode();
        node.put("packet_count", flowData.getPacketCount());
        node.put("byte_count", flowData.getByteCount());
        node.put("duration_ms", flowData.getDurationMillis());
        node.put("src_ip", key.getSrcIp());
        node.put("dst_ip", key.getDstIp());
        node.put("protocol", key.getProtocol());
        return node;
    }
}
