package com.iotids.networkengine.config;

public class BackendConfig {
    private String apiUrl = "http://localhost:8080/api/alerts";
    private boolean enabled = true;

    public String getApiUrl() { return apiUrl; }
    public void setApiUrl(String apiUrl) { this.apiUrl = apiUrl; }

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
}
