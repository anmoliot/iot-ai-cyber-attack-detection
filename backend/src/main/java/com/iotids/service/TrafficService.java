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
