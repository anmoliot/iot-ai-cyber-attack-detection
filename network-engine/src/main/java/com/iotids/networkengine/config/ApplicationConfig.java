package com.iotids.networkengine.config;

public class ApplicationConfig {
    private final CaptureConfig captureConfig = new CaptureConfig();
    private final FlowConfig flowConfig = new FlowConfig();
    private final MlConfig mlConfig = new MlConfig();
    private final BackendConfig backendConfig = new BackendConfig();

    public CaptureConfig getCaptureConfig() { return captureConfig; }
    public FlowConfig getFlowConfig() { return flowConfig; }
    public MlConfig getMlConfig() { return mlConfig; }
    public BackendConfig getBackendConfig() { return backendConfig; }
}
