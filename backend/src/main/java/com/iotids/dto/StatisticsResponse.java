package com.iotids.dto;
import lombok.*;
import java.util.Map;
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StatisticsResponse {
    private Long totalTraffic;
    private Long normalTraffic;
    private Long attackTraffic;
    private Long totalAttacks;
    private Long blockedIps;
    private Map<String, Long> attackDistribution;
    private Map<String, Long> protocolDistribution;
    private Map<String, Long> severityDistribution;
}
