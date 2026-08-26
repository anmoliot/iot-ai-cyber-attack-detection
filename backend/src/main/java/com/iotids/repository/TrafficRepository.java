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
