package com.iotids.backend.model;

import javax.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "alerts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Alert {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private LocalDateTime timestamp;
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "attack_id")
    private Attack attack;
    @Enumerated(EnumType.STRING)
    private AttackSeverity severity;
    private String message;
    @Enumerated(EnumType.STRING)
    private AlertStatus status;
    private LocalDateTime createdAt = LocalDateTime.now();
    private LocalDateTime acknowledgedAt;
}
