package com.iotids.networkengine.ml;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.iotids.networkengine.config.MlConfig;
import com.iotids.networkengine.feature.FeatureVector;
import com.iotids.networkengine.logging.NetworkLogger;
import okhttp3.*;

import java.io.IOException;

public class MlClient {
    private static final NetworkLogger logger = NetworkLogger.getLogger(MlClient.class);
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    
    private final MlConfig config;
    private final OkHttpClient client;
    private final ObjectMapper mapper;

    public MlClient(MlConfig config) {
        this.config = config;
        this.client = new OkHttpClient();
        this.mapper = new ObjectMapper();
    }

    public Prediction predict(FeatureVector features) {
        if (!config.isEnabled()) {
            return null;
        }

        try {
            ObjectNode payload = mapper.createObjectNode();
            payload.put("packet_count", features.getPacketCount());
            payload.put("byte_count", features.getByteCount());
            payload.put("duration_ms", features.getDurationMs());
            payload.put("src_ip", features.getSrcIp());
            payload.put("dst_ip", features.getDstIp());
            payload.put("protocol", features.getProtocol());

            String jsonPayload = mapper.writeValueAsString(payload);
            RequestBody body = RequestBody.create(jsonPayload, JSON);
            Request request = new Request.Builder()
                    .url(config.getApiUrl())
                    .post(body)
                    .build();

            logger.info("Sending FeatureVector to Python ML Service at " + config.getApiUrl());
            try (Response response = client.newCall(request).execute()) {
                if (response.isSuccessful() && response.body() != null) {
                    String responseBody = response.body().string();
                    JsonNode node = mapper.readTree(responseBody);
                    
                    Prediction prediction = new Prediction();
                    prediction.setAttack(node.path("is_attack").asBoolean(false));
                    prediction.setConfidence(node.path("confidence").asDouble(0.0));
                    prediction.setAttackType(node.path("attack_type").asText("Unknown"));
                    return prediction;
                } else {
                    logger.error("Python ML Service request failed: " + response.code());
                }
            }
        } catch (IOException e) {
            logger.error("Error communicating with Python ML Service: " + e.getMessage());
        }
        return null;
    }
}
