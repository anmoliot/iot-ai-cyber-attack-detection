package com.iotids.networkengine.decision;

import com.iotids.networkengine.flow.FlowData;
import com.iotids.networkengine.ml.Prediction;

public class DetectionDecision {
    private final FlowData flowData;
    private final Prediction prediction;
    private final boolean shouldBlock;

    public DetectionDecision(FlowData flowData, Prediction prediction, boolean shouldBlock) {
        this.flowData = flowData;
        this.prediction = prediction;
        this.shouldBlock = shouldBlock;
    }

    public FlowData getFlowData() { return flowData; }
    public Prediction getPrediction() { return prediction; }
    public boolean isShouldBlock() { return shouldBlock; }
}
