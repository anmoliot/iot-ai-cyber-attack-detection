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
