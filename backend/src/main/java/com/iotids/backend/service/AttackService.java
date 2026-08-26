package com.iotids.backend.service;

import com.iotids.backend.dto.*;
import com.iotids.backend.model.*;
import com.iotids.backend.repository.*;
import com.iotids.backend.websocket.AlertWebSocketHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class AttackService {
    @Autowired private AttackRepository attackRepo;
    @Autowired private AlertRepository alertRepo;
    @Autowired private AlertWebSocketHandler wsHandler;

    @Transactional
    public AttackResponse recordAttack(AttackRequest req) {
        Attack attack = Attack.builder()
                .timestamp(req.getTimestamp())
                .srcIp(req.getSrcIp())
                .dstIp(req.getDstIp())
                .srcPort(req.getSrcPort())
                .dstPort(req.getDstPort())
                .protocol(Protocol.valueOf(req.getProtocol()))
                .attackType(req.getAttackType())
                .confidence(req.getConfidence())
                .action(req.getAction())
                .severity(AttackSeverity.valueOf(req.getSeverity()))
                .status(AttackStatus.valueOf(req.getStatus()))
                .build();
        Attack saved = attackRepo.save(attack);
        Alert alert = Alert.builder()
                .timestamp(LocalDateTime.now())
                .attack(saved)
                .severity(saved.getSeverity())
                .message(String.format("%s attack detected from %s", saved.getAttackType(), saved.getSrcIp()))
                .status(AlertStatus.UNREAD)
                .build();
        alertRepo.save(alert);
        wsHandler.broadcastAlert(alert);
        return AttackResponse.builder()
                .success(true)
                .message("Attack event recorded")
                .attackId(saved.getId())
                .build();
    }
    public Page<Attack> listAttacks(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("timestamp").descending());
        return attackRepo.findAll(pageable);
    }
    public Optional<Attack> getAttack(Long id) { return attackRepo.findById(id); }
    public List<Attack> recentAttacks() { return attackRepo.findTop5ByOrderByTimestampDesc(); }
}
