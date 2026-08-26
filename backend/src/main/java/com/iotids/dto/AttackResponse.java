package com.iotids.dto;
import lombok.*;
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AttackResponse {
    private boolean success;
    private String message;
    private Long attackId;
}
