package com.iotids.controller;
import com.iotids.model.Alert;
import com.iotids.service.AlertService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController
@RequestMapping("/api/alerts")
public class AlertController {
    @Autowired private AlertService alertService;
    @GetMapping
    public ResponseEntity<Page<Alert>> list(@RequestParam(defaultValue = "0") int page,
                                            @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(alertService.listAlerts(page, size));
    }
    @GetMapping("/unread")
    public ResponseEntity<List<Alert>> unread() { return ResponseEntity.ok(alertService.unreadAlerts()); }
    @PutMapping("/{id}/read")
    public ResponseEntity<Void> markRead(@PathVariable Long id) { alertService.markAsRead(id); return ResponseEntity.noContent().build(); }
    @PutMapping("/{id}/acknowledge")
    public ResponseEntity<Void> acknowledge(@PathVariable Long id) { alertService.acknowledge(id); return ResponseEntity.noContent().build(); }
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) { alertService.deleteAlert(id); return ResponseEntity.noContent().build(); }
}
