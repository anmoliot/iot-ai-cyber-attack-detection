package com.iotids.networkengine.feature;

import com.iotids.networkengine.flow.FlowData;
import com.iotids.networkengine.flow.FlowKey;

/**
 * Builds a FeatureVector from a FlowData instance.
 */
public class FeatureBuilder {

    public FeatureVector buildFeature(FlowData flowData) {
        FlowKey key = flowData.getKey();
        return new FeatureVector(
            flowData.getPacketCount(),
            flowData.getByteCount(),
            flowData.getDurationMillis(),
            key.getSrcIp(),
            key.getDstIp(),
            key.getProtocol()
        );
    }
}
