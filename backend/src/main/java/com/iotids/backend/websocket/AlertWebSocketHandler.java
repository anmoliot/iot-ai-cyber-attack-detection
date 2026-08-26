package com.iotids.backend.websocket;
import com.iotids.backend.model.Alert;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;
@Component
@Slf4j
public class AlertWebSocketHandler {
    private final SimpMessagingTemplate messagingTemplate;
    public AlertWebSocketHandler(SimpMessagingTemplate messagingTemplate) { this.messagingTemplate = messagingTemplate; }
    public void broadcastAlert(Alert alert) {
        log.info("Broadcasting alert {}", alert.getId());
        messagingTemplate.convertAndSend("/topic/alerts", alert);
    }
}
