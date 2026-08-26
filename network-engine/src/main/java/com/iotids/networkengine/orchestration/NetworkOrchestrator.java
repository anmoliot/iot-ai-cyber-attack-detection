package com.iotids.networkengine.orchestration;


import com.iotids.networkengine.backend.BackendClient;
import com.iotids.networkengine.capture.CaptureManager;
import com.iotids.networkengine.capture.PacketListener;
import com.iotids.networkengine.config.ApplicationConfig;
import com.iotids.networkengine.decision.DecisionEngine;
import com.iotids.networkengine.decision.DetectionDecision;
import com.iotids.networkengine.feature.FeatureBuilder;
import com.iotids.networkengine.feature.FeatureVector;
import com.iotids.networkengine.flow.FlowCache;
import com.iotids.networkengine.flow.FlowData;
import com.iotids.networkengine.flow.FlowExpirationManager;
import com.iotids.networkengine.flow.FlowManager;
import com.iotids.networkengine.logging.NetworkLogger;
import com.iotids.networkengine.ml.MlClient;
import com.iotids.networkengine.ml.Prediction;
import com.iotids.networkengine.packet.PacketParser;
import com.iotids.networkengine.packet.ParsedPacket;
import com.iotids.networkengine.response.DryRunFirewallService;
import com.iotids.networkengine.response.ResponseManager;
import org.pcap4j.packet.Packet;

public class NetworkOrchestrator {
    private static final NetworkLogger logger = NetworkLogger.getLogger(NetworkOrchestrator.class);
    
    private final ApplicationConfig config;
    private final FlowCache flowCache;
    private final FlowManager flowManager;
    private final FeatureBuilder featureBuilder;
    private final MlClient mlClient;
    private final DecisionEngine decisionEngine;
    private final ResponseManager responseManager;
    
    private CaptureManager captureManager;
    private FlowExpirationManager expirationManager;
    private Thread expirationThread;

    public NetworkOrchestrator(ApplicationConfig config) {
        this.config = config;
        this.flowCache = new FlowCache();
        this.flowManager = new FlowManager(flowCache);
        this.featureBuilder = new FeatureBuilder();
        this.mlClient = new MlClient(config.getMlConfig());
        this.decisionEngine = new DecisionEngine(config.getMlConfig());
        
        BackendClient backendClient = new BackendClient(config.getBackendConfig());
        DryRunFirewallService firewallService = new DryRunFirewallService();
        this.responseManager = new ResponseManager(backendClient, firewallService);
    }

    public void start() {
        logger.info("Starting Network Orchestrator...");

        // Setup Flow Expiration (Handles completed flows)
        expirationManager = new FlowExpirationManager(flowCache, config.getFlowConfig(), this::handleExpiredFlow);
        expirationThread = new Thread(expirationManager, "FlowExpiration-Thread");
        expirationThread.start();

        // Setup Packet Capture (Handles new packets)
        PacketListener packetListener = this::handleRawPacket;
        captureManager = new CaptureManager(config.getCaptureConfig(), packetListener);
        captureManager.start();

        logger.info("Network Orchestrator fully started and listening for traffic.");
    }

    public void stop() {
        logger.info("Stopping Network Orchestrator...");
        if (captureManager != null) {
            captureManager.stop();
        }
        if (expirationManager != null) {
            expirationManager.stop();
        }
    }

    private void handleRawPacket(Packet rawPacket) {
        ParsedPacket parsed = PacketParser.parse(rawPacket);
        if (parsed != null) {
            flowManager.processPacket(parsed);
        }
    }

    private void handleExpiredFlow(FlowData flow) {
        // 1. Extract Features
        FeatureVector features = featureBuilder.buildFeature(flow);
        
        // 2. Query ML Model
        Prediction prediction = mlClient.predict(features);
        
        if (prediction != null) {
            // 3. Make Decision
            DetectionDecision decision = decisionEngine.evaluate(flow, prediction);
            
            // 4. Trigger Response (Backend Alert + Firewall Block)
            responseManager.handleDecision(decision);
        }
    }
}
