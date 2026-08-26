package com.iotids.backend.service;
import com.iotids.backend.dto.StatisticsResponse;
import com.iotids.backend.model.*;
import com.iotids.backend.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.*;
import java.util.stream.Collectors;
@Service
public class StatisticsService {
    @Autowired private AttackRepository attackRepo;
    @Autowired private TrafficRepository trafficRepo;
    @Autowired private AlertRepository alertRepo;
    public StatisticsResponse getStatistics() {
        long totalAttacks = attackRepo.count();
        long totalTraffic = trafficRepo.count();
        long attackTraffic = totalAttacks; // placeholder
        long normalTraffic = totalTraffic - attackTraffic;
        long blockedIps = attackRepo.findAll().stream()
                .filter(a -> "BLOCKED".equalsIgnoreCase(a.getAction()))
                .map(Attack::getSrcIp)
                .distinct().count();
        Map<String, Long> attackDist = attackRepo.findAll().stream()
                .collect(Collectors.groupingBy(Attack::getAttackType, Collectors.counting()));
        Map<String, Long> protocolDist = attackRepo.findAll().stream()
                .collect(Collectors.groupingBy(a -> a.getProtocol().name(), Collectors.counting()));
        Map<String, Long> severityDist = attackRepo.findAll().stream()
                .collect(Collectors.groupingBy(a -> a.getSeverity().name(), Collectors.counting()));
        return StatisticsResponse.builder()
                .totalAttacks(totalAttacks)
                .totalTraffic(totalTraffic)
                .attackTraffic(attackTraffic)
                .normalTraffic(normalTraffic)
                .blockedIps(blockedIps)
                .attackDistribution(attackDist)
                .protocolDistribution(protocolDist)
                .severityDistribution(severityDist)
                .build();
    }
}
