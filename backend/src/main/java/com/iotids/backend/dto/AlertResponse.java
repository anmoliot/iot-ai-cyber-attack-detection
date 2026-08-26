package com.iotids.backend.dto;

import com.iotids.backend.model.AlertStatus;
import java.time.LocalDateTime;

public class AlertResponse {
    private Long id;
    private String title;
    private String description;
    private AlertStatus status;
    private LocalDateTime timestamp;

    public AlertResponse() {}

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public AlertStatus getStatus() { return status; }
    public void setStatus(AlertStatus status) { this.status = status; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
