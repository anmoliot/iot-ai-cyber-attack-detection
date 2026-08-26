package com.iotids.networkengine.flow;

import com.iotids.networkengine.config.FlowConfig;
import com.iotids.networkengine.logging.NetworkLogger;

import java.util.List;
import java.util.function.Consumer;

public class FlowExpirationManager implements Runnable {
    private static final NetworkLogger logger = NetworkLogger.getLogger(FlowExpirationManager.class);
    
    private final FlowCache flowCache;
    private final FlowConfig flowConfig;
    private final Consumer<FlowData> onFlowExpired;
    private volatile boolean running = false;

    public FlowExpirationManager(FlowCache flowCache, FlowConfig flowConfig, Consumer<FlowData> onFlowExpired) {
        this.flowCache = flowCache;
        this.flowConfig = flowConfig;
        this.onFlowExpired = onFlowExpired;
    }

    public void stop() {
        running = false;
    }

    @Override
    public void run() {
        running = true;
        logger.info("FlowExpirationManager started");
        
        while (running) {
            try {
                Thread.sleep(flowConfig.getCleanupIntervalMs());
                
                List<FlowData> expiredFlows = flowCache.getExpiredFlows(flowConfig.getFlowTimeoutMs());
                for (FlowData flow : expiredFlows) {
                    flowCache.remove(flow.getKey());
                    onFlowExpired.accept(flow);
                }
                
                if (expiredFlows.size() > 0) {
                    logger.debug("Expired " + expiredFlows.size() + " flows.");
                }
                
            } catch (InterruptedException e) {
                running = false;
                Thread.currentThread().interrupt();
            }
        }
    }
}
