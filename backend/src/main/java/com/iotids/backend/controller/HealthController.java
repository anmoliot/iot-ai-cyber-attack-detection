package com.iotids.backend.controller;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthEndpoint;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final HealthEndpoint healthEndpoint;

    public HealthController(HealthEndpoint healthEndpoint) {
        this.healthEndpoint = healthEndpoint;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Health health = (Health) healthEndpoint.health();
        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("status", health.getStatus().getCode());
        resp.put("application", "IoT IDS Backend");
        resp.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(resp);
    }
}
