package com.iotids.networkengine.ml;

public class Prediction {
    private boolean isAttack;
    private double confidence;
    private String attackType;

    public boolean isAttack() { return isAttack; }
    public void setAttack(boolean attack) { isAttack = attack; }

    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }

    public String getAttackType() { return attackType; }
    public void setAttackType(String attackType) { this.attackType = attackType; }
}
