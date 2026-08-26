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
