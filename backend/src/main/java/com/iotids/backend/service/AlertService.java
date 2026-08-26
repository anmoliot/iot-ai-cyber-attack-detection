package com.iotids.backend.service;
import com.iotids.backend.model.Alert;
import com.iotids.backend.model.AlertStatus;
import com.iotids.backend.repository.AlertRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class AlertService {
    @Autowired private AlertRepository alertRepo;
    public Page<Alert> listAlerts(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("timestamp").descending());
        return alertRepo.findAll(pageable);
    }
    public List<Alert> unreadAlerts() {
        return alertRepo.findAllByStatus(AlertStatus.UNREAD, PageRequest.of(0, 100)).getContent();
    }
    public void markAsRead(Long id) { alertRepo.findById(id).ifPresent(a -> { a.setStatus(AlertStatus.READ); alertRepo.save(a); }); }
    public void acknowledge(Long id) { alertRepo.findById(id).ifPresent(a -> { a.setStatus(AlertStatus.ACKNOWLEDGED); a.setAcknowledgedAt(java.time.LocalDateTime.now()); alertRepo.save(a); }); }
    public void deleteAlert(Long id) { alertRepo.deleteById(id); }
}
