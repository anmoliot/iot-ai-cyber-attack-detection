package com.iotids.networkengine.backend;

public class AttackEvent {
    private final String sourceIp;
    private final String targetIp;
    private final String type;
    private final String severity;

    public AttackEvent(String sourceIp, String targetIp, String type, String severity) {
        this.sourceIp = sourceIp;
        this.targetIp = targetIp;
        this.type = type;
        this.severity = severity;
    }

    public String getSourceIp() { return sourceIp; }
    public String getTargetIp() { return targetIp; }
    public String getType() { return type; }
    public String getSeverity() { return severity; }
}
