package com.iotids.networkengine.decision;

import com.iotids.networkengine.config.MlConfig;
import com.iotids.networkengine.flow.FlowData;
import com.iotids.networkengine.ml.Prediction;
import com.iotids.networkengine.logging.NetworkLogger;

public class DecisionEngine {
    private static final NetworkLogger logger = NetworkLogger.getLogger(DecisionEngine.class);
    private final MlConfig config;

    public DecisionEngine(MlConfig config) {
        this.config = config;
    }

    public DetectionDecision evaluate(FlowData flow, Prediction prediction) {
        if (prediction == null) {
            return null;
        }

        boolean shouldBlock = false;
        
        if (prediction.isAttack()) {
            if (prediction.getConfidence() >= config.getConfidenceThreshold()) {
                logger.warn(String.format("HIGH CONFIDENCE ATTACK DETECTED: %s from %s (Confidence: %.2f)", 
                        prediction.getAttackType(), flow.getKey().getSrcIp(), prediction.getConfidence()));
                shouldBlock = true;
            } else {
                logger.info(String.format("Low confidence attack detected: %s from %s (Confidence: %.2f). Not blocking.", 
                        prediction.getAttackType(), flow.getKey().getSrcIp(), prediction.getConfidence()));
            }
        }

        return new DetectionDecision(flow, prediction, shouldBlock);
    }
}
