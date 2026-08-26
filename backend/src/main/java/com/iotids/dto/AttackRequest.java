package com.iotids.dto;

import javax.validation.constraints.*;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AttackRequest {
    @NotNull
    private LocalDateTime timestamp;
    @Pattern(regexp = "^([0-9]{1,3}\\.){3}[0-9]{1,3}$")
    private String srcIp;
    @Pattern(regexp = "^([0-9]{1,3}\\.){3}[0-9]{1,3}$")
    private String dstIp;
    @Min(0) @Max(65535)
    private Integer srcPort;
    @Min(0) @Max(65535)
    private Integer dstPort;
    @NotBlank
    private String protocol;
    @NotBlank
    private String attackType;
    @DecimalMin("0.0") @DecimalMax("1.0")
    private Double confidence;
    @NotBlank
    private String action;
    @NotBlank
    private String severity;
    @NotBlank
    private String status;
}
