package com.iotids.networkengine.flow;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.ArrayList;

public class FlowCache {
    private final Map<FlowKey, FlowData> cache = new ConcurrentHashMap<>();

    public FlowData getOrCreate(FlowKey key, long timestamp) {
        return cache.computeIfAbsent(key, k -> new FlowData(k, timestamp));
    }

    public FlowData get(FlowKey key) {
        return cache.get(key);
    }

    public void remove(FlowKey key) {
        cache.remove(key);
    }

    public List<FlowData> getExpiredFlows(long timeoutMs) {
        long now = System.currentTimeMillis();
        List<FlowData> expired = new ArrayList<>();
        
        for (Map.Entry<FlowKey, FlowData> entry : cache.entrySet()) {
            if ((now - entry.getValue().getLastSeenTime()) > timeoutMs) {
                expired.add(entry.getValue());
            }
        }
        return expired;
    }
}
