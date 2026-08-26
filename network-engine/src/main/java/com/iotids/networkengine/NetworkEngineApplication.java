package com.iotids.networkengine;

import com.iotids.networkengine.config.ApplicationConfig;
import com.iotids.networkengine.logging.NetworkLogger;
import com.iotids.networkengine.orchestration.NetworkOrchestrator;

public class NetworkEngineApplication {
    private static final NetworkLogger logger = NetworkLogger.getLogger(NetworkEngineApplication.class);

    public static void main(String[] args) {
        logger.info("Starting Network Engine Application");
        ApplicationConfig config = new ApplicationConfig(); // placeholder
        NetworkOrchestrator orchestrator = new NetworkOrchestrator(config);
        orchestrator.start();
        Runtime.getRuntime().addShutdownHook(new Thread(orchestrator::stop));
    }
}
