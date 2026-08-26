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
