package com.iotids.backend.model;

import javax.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "traffic")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Traffic {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private LocalDateTime timestamp;
    private String srcIp;
    private String dstIp;
    @Enumerated(EnumType.STRING)
    private Protocol protocol;
    private Long packetCount;
    private Long byteCount;
    private Double duration;
    private Double averagePacketSize;
    private Double packetRate;
    private Double byteRate;
    private String classification;
    private LocalDateTime createdAt = LocalDateTime.now();
}
