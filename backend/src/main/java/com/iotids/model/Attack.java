package com.iotids.model;

import javax.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "attacks")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Attack {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private LocalDateTime timestamp;
    private String srcIp;
    private String dstIp;
    private Integer srcPort;
    private Integer dstPort;
    @Enumerated(EnumType.STRING)
    private Protocol protocol;
    private String attackType;
    private Double confidence;
    private String action;
    @Enumerated(EnumType.STRING)
    private AttackSeverity severity;
    @Enumerated(EnumType.STRING)
    private AttackStatus status;
    private LocalDateTime createdAt = LocalDateTime.now();
}
