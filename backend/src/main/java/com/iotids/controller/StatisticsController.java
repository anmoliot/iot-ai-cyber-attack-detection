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
