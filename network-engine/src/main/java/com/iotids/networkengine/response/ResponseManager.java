package com.iotids.networkengine.response;

import com.iotids.networkengine.backend.AttackEvent;
import com.iotids.networkengine.backend.BackendClient;
import com.iotids.networkengine.decision.DetectionDecision;
import com.iotids.networkengine.logging.NetworkLogger;

public class ResponseManager {
    private static final NetworkLogger logger = NetworkLogger.getLogger(ResponseManager.class);
    private final BackendClient backendClient;
    private final DryRunFirewallService firewallService;

    public ResponseManager(BackendClient backendClient, DryRunFirewallService firewallService) {
        this.backendClient = backendClient;
        this.firewallService = firewallService;
    }

    public void handleDecision(DetectionDecision decision) {
        if (decision == null || decision.getPrediction() == null) return;

        if (decision.getPrediction().isAttack()) {
            String attackerIp = decision.getFlowData().getKey().getSrcIp();
            String targetIp = decision.getFlowData().getKey().getDstIp();
            String attackType = decision.getPrediction().getAttackType();
            String severity = decision.isShouldBlock() ? "HIGH" : "MEDIUM";
            
            logger.info("Handling attack response for IP: " + attackerIp);

            // 1. Send alert to backend dashboard
            AttackEvent event = new AttackEvent(attackerIp, targetIp, attackType, severity);
            backendClient.sendAttackEvent(event);

            // 2. Block IP if required
            if (decision.isShouldBlock()) {
                firewallService.blockIp(attackerIp);
            }
        }
    }
}
