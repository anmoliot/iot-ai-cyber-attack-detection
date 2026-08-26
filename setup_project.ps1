# PowerShell script to bootstrap the AI‑Based Cyber Attack Detection project
# Run this script in an elevated PowerShell session.

$base = "C:\Users\Anmol\OneDrive\Desktop\AI Based Cyber Attack Detection"

# Helper to create directories if they don't exist
function Ensure-Dir($path) {
    if (-Not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

# -------------------------------------------------------------------
# 1. Create main folder structure
# -------------------------------------------------------------------
Ensure-Dir $base
Ensure-Dir "$base\backend"
Ensure-Dir "$base\backend\src"
Ensure-Dir "$base\backend\src\main"
Ensure-Dir "$base\backend\src\main\java"
Ensure-Dir "$base\backend\src\main\java\com"
Ensure-Dir "$base\backend\src\main\java\com\iotids"
Ensure-Dir "$base\backend\src\main\resources"
Ensure-Dir "$base\backend\src\main\resources\static"
Ensure-Dir "$base\backend\src\main\resources\static\css"
Ensure-Dir "$base\backend\src\main\resources\static\js"
Ensure-Dir "$base\backend\src\test"
Ensure-Dir "$base\backend\src\test\java"
Ensure-Dir "$base\backend\src\test\java\com"
Ensure-Dir "$base\backend\src\test\java\com\iotids"
Ensure-Dir "$base\backend\docs"
Ensure-Dir "$base\backend\tasks"

# -------------------------------------------------------------------
# 2. Write backend files (Maven pom, application, config, etc.)
# -------------------------------------------------------------------
# pom.xml
@'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.iotids</groupId>
    <artifactId>iotids-backend</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    <name>IoT IDS Backend</name>
    <description>AI‑Based Cyber Attack Detection System for IoT Devices</description>
    <properties>
        <java.version>21</java.version>
        <spring.boot.version>3.2.2</spring.boot.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-websocket</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${spring.boot.version}</version>
            </plugin>
        </plugins>
    </build>
</project>
'@ | Set-Content -Path "$base\backend\pom.xml" -Encoding UTF8

# Application entry point
@'
package com.iotids;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class IotIdsApplication {
    public static void main(String[] args) {
        SpringApplication.run(IotIdsApplication.class, args);
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\IotIdsApplication.java" -Encoding UTF8

# Enums
@'
package com.iotids.model;
public enum Protocol { TCP, UDP, ICMP, OTHER }
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\Protocol.java" -Encoding UTF8

@'
package com.iotids.model;
public enum AttackSeverity { LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN }
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\AttackSeverity.java" -Encoding UTF8

@'
package com.iotids.model;
public enum AttackStatus { DETECTED, BLOCKED, MITIGATED, IGNORED }
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\AttackStatus.java" -Encoding UTF8

@'
package com.iotids.model;
public enum AlertStatus { UNREAD, READ, ACKNOWLEDGED }
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\AlertStatus.java" -Encoding UTF8

# Entities
@'
package com.iotids.model;

import jakarta.persistence.*;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\Attack.java" -Encoding UTF8

@'
package com.iotids.model;

import jakarta.persistence.*;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\Traffic.java" -Encoding UTF8

@'
package com.iotids.model;

import jakarta.persistence.*;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\model\Alert.java" -Encoding UTF8

# Repositories
@'
package com.iotids.repository;

import com.iotids.model.Attack;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AttackRepository extends JpaRepository<Attack, Long> {
    Page<Attack> findAllByTimestampBetween(LocalDateTime start, LocalDateTime end, Pageable pageable);
    List<Attack> findTop5ByOrderByTimestampDesc();
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\repository\AttackRepository.java" -Encoding UTF8

@'
package com.iotids.repository;

import com.iotids.model.Traffic;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface TrafficRepository extends JpaRepository<Traffic, Long> {
    Page<Traffic> findAllByTimestampBetween(LocalDateTime start, LocalDateTime end, Pageable pageable);
    List<Traffic> findTop5ByOrderByTimestampDesc();
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\repository\TrafficRepository.java" -Encoding UTF8

@'
package com.iotids.repository;

import com.iotids.model.Alert;
import com.iotids.model.AttackSeverity;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface AlertRepository extends JpaRepository<Alert, Long> {
    Page<Alert> findAllByStatus(com.iotids.model.AlertStatus status, Pageable pageable);
    List<Alert> findTop5ByOrderByTimestampDesc();
    List<Alert> findBySeverity(AttackSeverity severity);
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\repository\AlertRepository.java" -Encoding UTF8

# DTOs
@'
package com.iotids.dto;

import jakarta.validation.constraints.*;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\dto\AttackRequest.java" -Encoding UTF8

@'
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\dto\AttackResponse.java" -Encoding UTF8

@'
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\dto\StatisticsResponse.java" -Encoding UTF8

# Services
@'
package com.iotids.service;

import com.iotids.dto.*;
import com.iotids.model.*;
import com.iotids.repository.*;
import com.iotids.websocket.AlertWebSocketHandler;
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
                .message("%s attack detected from %s".formatted(saved.getAttackType(), saved.getSrcIp()))
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\service\AttackService.java" -Encoding UTF8

@'
package com.iotids.service;
import com.iotids.model.Traffic;
import com.iotids.repository.TrafficRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.*;
@Service
public class TrafficService {
    @Autowired private TrafficRepository trafficRepo;
    public Traffic saveTraffic(Traffic traffic) { return trafficRepo.save(traffic); }
    public Page<Traffic> listTraffic(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("timestamp").descending());
        return trafficRepo.findAll(pageable);
    }
    public List<Traffic> recentTraffic() { return trafficRepo.findTop5ByOrderByTimestampDesc(); }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\service\TrafficService.java" -Encoding UTF8

@'
package com.iotids.service;
import com.iotids.dto.StatisticsResponse;
import com.iotids.model.*;
import com.iotids.repository.*;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\service\StatisticsService.java" -Encoding UTF8

@'
package com.iotids.service;
import com.iotids.model.Alert;
import com.iotids.model.AlertStatus;
import com.iotids.repository.AlertRepository;
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\service\AlertService.java" -Encoding UTF8

# Controllers
@'
package com.iotids.controller;
import com.iotids.dto.*;
import com.iotids.model.Attack;
import com.iotids.service.AttackService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController
@RequestMapping("/api/attacks")
public class AttackController {
    @Autowired private AttackService attackService;
    @PostMapping
    public ResponseEntity<AttackResponse> create(@Valid @RequestBody AttackRequest request) {
        AttackResponse resp = attackService.recordAttack(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(resp);
    }
    @GetMapping
    public ResponseEntity<Page<Attack>> list(@RequestParam(defaultValue = "0") int page,
                                             @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(attackService.listAttacks(page, size));
    }
    @GetMapping("/recent")
    public ResponseEntity<List<Attack>> recent() { return ResponseEntity.ok(attackService.recentAttacks()); }
    @GetMapping("/{id}")
    public ResponseEntity<Attack> get(@PathVariable Long id) {
        return attackService.getAttack(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\controller\AttackController.java" -Encoding UTF8

@'
package com.iotids.controller;
import com.iotids.model.Traffic;
import com.iotids.service.TrafficService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController
@RequestMapping("/api/traffic")
public class TrafficController {
    @Autowired private TrafficService trafficService;
    @PostMapping
    public ResponseEntity<Traffic> record(@RequestBody Traffic traffic) {
        return new ResponseEntity<>(trafficService.saveTraffic(traffic), HttpStatus.CREATED);
    }
    @GetMapping
    public ResponseEntity<Page<Traffic>> list(@RequestParam(defaultValue = "0") int page,
                                              @RequestParam(defaultValue = "20") int size) {
        return ResponseEntity.ok(trafficService.listTraffic(page, size));
    }
    @GetMapping("/recent")
    public ResponseEntity<List<Traffic>> recent() { return ResponseEntity.ok(trafficService.recentTraffic()); }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\controller\TrafficController.java" -Encoding UTF8

@'
package com.iotids.controller;
import com.iotids.dto.StatisticsResponse;
import com.iotids.service.StatisticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
@RestController
@RequestMapping("/api/statistics")
public class StatisticsController {
    @Autowired private StatisticsService statisticsService;
    @GetMapping
    public ResponseEntity<StatisticsResponse> getAll() { return ResponseEntity.ok(statisticsService.getStatistics()); }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\controller\StatisticsController.java" -Encoding UTF8

@'
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
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\controller\AlertController.java" -Encoding UTF8

@'
package com.iotids.controller;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthEndpoint;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.*;
@RestController
@RequestMapping("/api/health")
public class HealthController {
    private final HealthEndpoint healthEndpoint;
    public HealthController(HealthEndpoint healthEndpoint) { this.healthEndpoint = healthEndpoint; }
    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Health health = healthEndpoint.health();
        Map<String, Object> resp = new LinkedHashMap<>();
        resp.put("status", health.getStatus().getCode());
        resp.put("application", "IoT IDS Backend");
        resp.put("timestamp", LocalDateTime.now());
        return ResponseEntity.ok(resp);
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\controller\HealthController.java" -Encoding UTF8

# Configurations
@'
package com.iotids.config;
import org.springframework.context.annotation.*;
import org.springframework.web.cors.*;
import org.springframework.web.filter.CorsFilter;
@Configuration
public class CorsConfig {
    @Bean
    public CorsFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOriginPattern("*");
        config.addAllowedHeader("*");
        config.addAllowedMethod("*");
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\config\CorsConfig.java" -Encoding UTF8

@'
package com.iotids.websocket;
import org.springframework.context.annotation.*;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.*;
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/topic");
        registry.setApplicationDestinationPrefixes("/app");
    }
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws").setAllowedOriginPatterns("*").withSockJS();
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\websocket\WebSocketConfig.java" -Encoding UTF8

@'
package com.iotids.websocket;
import com.iotids.model.Alert;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;
@Component
@Slf4j
public class AlertWebSocketHandler {
    private final SimpMessagingTemplate messagingTemplate;
    public AlertWebSocketHandler(SimpMessagingTemplate messagingTemplate) { this.messagingTemplate = messagingTemplate; }
    public void broadcastAlert(Alert alert) {
        log.info("Broadcasting alert {}", alert.getId());
        messagingTemplate.convertAndSend("/topic/alerts", alert);
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\websocket\AlertWebSocketHandler.java" -Encoding UTF8

@'
package com.iotids.config;
import org.springframework.context.annotation.*;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
@Configuration
public class SecurityConfig {
    @Bean
    public InMemoryUserDetailsManager userDetailsService(PasswordEncoder encoder) {
        UserDetails admin = User.builder()
                .username("admin")
                .password(encoder.encode(System.getenv("ADMIN_PASSWORD")))
                .roles("ADMIN")
                .build();
        return new InMemoryUserDetailsManager(admin);
    }
    @Bean
    public PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/**", "/ws/**", "/static/**", "/index.html").permitAll()
                .anyRequest().authenticated()
            )
            .httpBasic();
        return http.build();
    }
}
'@ | Set-Content -Path "$base\backend\src\main\java\com\iotids\config\SecurityConfig.java" -Encoding UTF8

# application.properties
@'
# DataSource configuration – values come from env vars
spring.datasource.url=${DB_URL}
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false

# Server
server.port=8080

# Logging
logging.level.root=INFO
logging.level.org.springframework=INFO
logging.level.com.iotids=DEBUG

# WebSocket path (SockJS fallback)
spring.websocket.path=/ws
'@ | Set-Content -Path "$base\backend\src\main\resources\application.properties" -Encoding UTF8

# Frontend files
@'
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IoT IDS Dashboard</title>
    <link rel="stylesheet" href="css/dashboard.css" />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sockjs-client@1/dist/sockjs.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/stompjs@2.3.3/lib/stomp.min.js"></script>
</head>
<body>
    <header class="top-nav">
        <h1>IoT IDS – Security Operations Center</h1>
        <div class="user-info"><span id="admin-name">Admin</span><button id="logout-btn">Logout</button></div>
    </header>
    <main class="dashboard">
        <section class="cards">
            <div class="card" id="total-traffic-card"><div class="icon">📊</div><div class="value" data-key="totalTraffic">0</div><div class="label">Total Traffic</div></div>
            <div class="card" id="normal-traffic-card"><div class="icon">✅</div><div class="value" data-key="normalTraffic">0</div><div class="label">Normal Traffic</div></div>
            <div class="card" id="attack-count-card"><div class="icon">⚠️</div><div class="value" data-key="totalAttacks">0</div><div class="label">Attacks Detected</div></div>
            <div class="card" id="blocked-sources-card"><div class="icon">🚫</div><div class="value" data-key="blockedIps">0</div><div class="label">Blocked Sources</div></div>
            <div class="card" id="critical-alerts-card"><div class="icon">🔥</div><div class="value" data-key="criticalAlerts">0</div><div class="label">Critical Alerts</div></div>
        </section>
        <section class="charts">
            <canvas id="attack-distribution-chart"></canvas>
            <canvas id="traffic-timeline-chart"></canvas>
            <canvas id="protocol-distribution-chart"></canvas>
            <canvas id="severity-distribution-chart"></canvas>
        </section>
        <section class="alert-panel" id="alert-panel"><h2>Real‑time Alerts</h2><ul id="alert-list"></ul></section>
        <section class="attack-table" id="attack-table-section"><h2>Recent Attacks</h2><table><thead><tr><th>Time</th><th>Source IP</th><th>Destination IP</th><th>Protocol</th><th>Type</th><th>Severity</th><th>Confidence</th><th>Action</th><th>Status</th></tr></thead><tbody id="attack-table-body"></tbody></table><div class="pagination" id="attack-pagination"></div></section>
    </main>
    <script src="js/api.js"></script>
    <script src="js/charts.js"></script>
    <script src="js/websocket.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
'@ | Set-Content -Path "$base\backend\src\main\resources\static\index.html" -Encoding UTF8

@'
/* Premium Hybrid – Light mode with subtle glassmorphism */
:root { --bg:#f5f7fa; --card-bg:rgba(255,255,255,0.85); --primary:#3b82f6; --accent:#10b981; --danger:#ef4444; --text:#1f2937; --text-dim:#6b7280; --shadow:0 4px 12px rgba(0,0,0,0.08); }
[data-theme="dark"] { --bg:#0f172a; --card-bg:rgba(31,41,55,0.85); --text:#e2e8f0; --text-dim:#94a3b8; }
body { margin:0; font-family:'Inter',system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.5; display:flex; flex-direction:column; min-height:100vh; }
.top-nav { display:flex; justify-content:space-between; align-items:center; padding:1rem 2rem; background:var(--card-bg); box-shadow:var(--shadow); }
.dashboard { padding:2rem; display:grid; gap:2rem; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
.cards { display:flex; flex-wrap:wrap; gap:1rem; }
.card { background:var(--card-bg); border-radius:0.75rem; padding:1.5rem; flex:1 1 150px; box-shadow:var(--shadow); transition:transform 0.2s; }
.card:hover { transform:translateY(-3px); }
.card .icon { font-size:1.5rem; margin-bottom:0.5rem; }
.card .value { font-size:2rem; font-weight:600; }
.charts canvas { width:100% !important; height:auto; margin-bottom:1.5rem; background:var(--card-bg); border-radius:0.75rem; padding:1rem; }
.alert-panel { background:var(--card-bg); border-radius:0.75rem; padding:1rem; box-shadow:var(--shadow); max-height:400px; overflow-y:auto; }
.alert-panel ul { list-style:none; margin:0; padding:0; }
.alert-panel li { padding:0.75rem; border-bottom:1px solid #e5e7eb; }
.alert-panel li.high { background:#fee2e2; }
.alert-panel li.medium { background:#fef3c7; }
.alert-panel li.low { background:#d1fae5; }
.attack-table table { width:100%; border-collapse:collapse; background:var(--card-bg); border-radius:0.75rem; overflow:hidden; }
.attack-table th, .attack-table td { padding:0.75rem; text-align:left; border-bottom:1px solid #e5e7eb; }
.attack-table th { background:#f3f4f6; }
.pagination { margin-top:1rem; display:flex; gap:0.5rem; }
.pagination button { padding:0.5rem 1rem; border:none; background:var(--primary); color:#fff; border-radius:0.25rem; cursor:pointer; }
@media (max-width:768px) { .dashboard { grid-template-columns:1fr; } }
'@ | Set-Content -Path "$base\backend\src\main\resources\static\css\dashboard.css" -Encoding UTF8

@'
export const API = {
    getStatistics: async () => { const r = await fetch('/api/statistics'); return r.json(); },
    getRecentAttacks: async (page = 0, size = 10) => { const r = await fetch(`/api/attacks?page=${page}&size=${size}`); return r.json(); },
    getRecentAlerts: async () => { const r = await fetch('/api/alerts/unread'); return r.json(); }
};
'@ | Set-Content -Path "$base\backend\src\main\resources\static\js\api.js" -Encoding UTF8

@'
import { API } from './api.js';
let attackChart, trafficChart, protocolChart, severityChart;
export async function renderCharts() {
    const stats = await API.getStatistics();
    const attackCtx = document.getElementById('attack-distribution-chart').getContext('2d');
    attackChart && attackChart.destroy();
    attackChart = new Chart(attackCtx, { type:'doughnut', data:{ labels:Object.keys(stats.attackDistribution), datasets:[{ data:Object.values(stats.attackDistribution), backgroundColor:['#3b82f6','#06b6d4','#8b5cf6','#10b981','#f97316','#ef4444','#eab308'], borderWidth:0 }]}, options:{ plugins:{ legend:{ position:'right' } } });
    const protoCtx = document.getElementById('protocol-distribution-chart').getContext('2d');
    protocolChart && protocolChart.destroy();
    protocolChart = new Chart(protoCtx, { type:'pie', data:{ labels:Object.keys(stats.protocolDistribution), datasets:[{ data:Object.values(stats.protocolDistribution), backgroundColor:['#3b82f6','#ef4444','#06b6d4'] }] } );
    const sevCtx = document.getElementById('severity-distribution-chart').getContext('2d');
    severityChart && severityChart.destroy();
    severityChart = new Chart(sevCtx, { type:'bar', data:{ labels:Object.keys(stats.severityDistribution), datasets:[{ label:'Attacks', data:Object.values(stats.severityDistribution), backgroundColor:'#f97316' }] } );
    const trafficCtx = document.getElementById('traffic-timeline-chart').getContext('2d');
    trafficChart && trafficChart.destroy();
    trafficChart = new Chart(trafficCtx, { type:'line', data:{ labels:Array.from({length:12},(_,i)=>`Jan ${i+1}`), datasets:[{ label:'Traffic', data:Array.from({length:12},()=>Math.floor(Math.random()*2000)+500), borderColor:'#10b981', fill:false }] } );
}
'@ | Set-Content -Path "$base\backend\src\main\resources\static\js\charts.js" -Encoding UTF8

@'
export function initWebSocket() {
    const socket = new SockJS('/ws');
    const stomp = Stomp.over(socket);
    stomp.connect({}, () => {
        stomp.subscribe('/topic/alerts', msg => { const alert = JSON.parse(msg.body); showAlert(alert); });
    });
}
function showAlert(alert) {
    const list = document.getElementById('alert-list');
    const li = document.createElement('li');
    li.className = alert.severity.toLowerCase();
    li.innerHTML = `<strong>${alert.severity}</strong> – ${alert.message}<br><small>${new Date(alert.timestamp).toLocaleString()}</small>`;
    list.prepend(li);
    setTimeout(() => li.remove(), 10000);
}
'@ | Set-Content -Path "$base\backend\src\main\resources\static\js\websocket.js" -Encoding UTF8

@'
import { API } from './api.js';
import { renderCharts } from './charts.js';
import { initWebSocket } from './websocket.js';
(async function init() { await renderCharts(); initWebSocket(); loadCards(); loadAttackTable(); })();
async function loadCards() { const stats = await API.getStatistics(); document.querySelectorAll('.card .value').forEach(el => { const key = el.dataset.key; if (stats[key] !== undefined) { el.textContent = stats[key]; } }); }
let currentPage = 0;
async function loadAttackTable(page = 0) {
    const data = await API.getRecentAttacks(page, 10);
    const tbody = document.getElementById('attack-table-body');
    tbody.innerHTML = '';
    data.content.forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(a.timestamp).toLocaleString()}</td><td>${a.srcIp}</td><td>${a.dstIp}</td><td>${a.protocol}</td><td>${a.attackType}</td><td>${a.severity}</td><td>${(a.confidence*100).toFixed(1)}%</td><td>${a.action}</td><td>${a.status}</td>`;
        tbody.appendChild(tr);
    });
    const pagination = document.getElementById('attack-pagination');
    pagination.innerHTML = '';
    const prev = document.createElement('button'); prev.textContent = 'Prev'; prev.disabled = page === 0; prev.onclick = () => loadAttackTable(page-1);
    const next = document.createElement('button'); next.textContent = 'Next'; next.disabled = !data.last; next.onclick = () => loadAttackTable(page+1);
    pagination.append(prev, next);
}
'@ | Set-Content -Path "$base\backend\src\main\resources\static\js\dashboard.js" -Encoding UTF8

# .env.example
@'
DB_URL=jdbc:mysql://localhost:3306/iotids
DB_USERNAME=root
DB_PASSWORD=your_password
ADMIN_PASSWORD=admin123
'@ | Set-Content -Path "$base\backend\.env.example" -Encoding UTF8

Write-Host "Bootstrap completed. To build the backend, open PowerShell, cd to $base\backend and run 'mvn clean install' then 'mvn spring-boot:run'."
