package com.iotids.networkengine.backend;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iotids.networkengine.config.BackendConfig;
import com.iotids.networkengine.logging.NetworkLogger;
import okhttp3.*;

import java.io.IOException;

public class BackendClient {
    private static final NetworkLogger logger = NetworkLogger.getLogger(BackendClient.class);
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    
    private final BackendConfig config;
    private final OkHttpClient client;
    private final ObjectMapper mapper;

    public BackendClient(BackendConfig config) {
        this.config = config;
        this.client = new OkHttpClient();
        this.mapper = new ObjectMapper();
    }

    public void sendAttackEvent(AttackEvent event) {
        if (!config.isEnabled()) return;

        try {
            String jsonPayload = mapper.writeValueAsString(event);
            RequestBody body = RequestBody.create(jsonPayload, JSON);
            Request request = new Request.Builder()
                    .url(config.getApiUrl())
                    .post(body)
                    .build();

            // Fire and forget (async)
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    logger.error("Failed to send attack event to backend: " + e.getMessage());
                }

                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    try {
                        if (!response.isSuccessful()) {
                            logger.error("Backend returned error: " + response.code());
                        } else {
                            logger.info("Attack event sent to backend successfully.");
                        }
                    } finally {
                        response.close();
                    }
                }
            });
        } catch (IOException e) {
            logger.error("Error creating backend request: " + e.getMessage());
        }
    }
}
