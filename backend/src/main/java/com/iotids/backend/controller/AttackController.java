package com.iotids.backend.controller;
import com.iotids.backend.dto.*;
import com.iotids.backend.model.Attack;
import com.iotids.backend.service.AttackService;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import java.util.*;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.PathVariable;
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
