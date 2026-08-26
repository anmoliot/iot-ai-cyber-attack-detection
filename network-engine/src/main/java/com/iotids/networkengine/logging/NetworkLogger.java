package com.iotids.networkengine.logging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class NetworkLogger {
    private final Logger logger;

    private NetworkLogger(Class<?> clazz) {
        this.logger = LoggerFactory.getLogger(clazz);
    }

    public static NetworkLogger getLogger(Class<?> clazz) {
        return new NetworkLogger(clazz);
    }

    public void info(String msg) { logger.info(msg); }
    public void warn(String msg) { logger.warn(msg); }
    public void error(String msg) { logger.error(msg); }
    public void error(String msg, Throwable t) { logger.error(msg, t); }
    public void debug(String msg) { logger.debug(msg); }
}
