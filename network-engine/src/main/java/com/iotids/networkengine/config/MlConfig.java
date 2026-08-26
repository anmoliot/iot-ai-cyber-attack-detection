package com.iotids.networkengine.config;

public class MlConfig {
    private String apiUrl = "http://localhost:5000/predict";
    private boolean enabled = true;
    private double confidenceThreshold = 0.85;

    public String getApiUrl() { return apiUrl; }
    public void setApiUrl(String apiUrl) { this.apiUrl = apiUrl; }

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }

    public double getConfidenceThreshold() { return confidenceThreshold; }
    public void setConfidenceThreshold(double confidenceThreshold) { this.confidenceThreshold = confidenceThreshold; }
}
