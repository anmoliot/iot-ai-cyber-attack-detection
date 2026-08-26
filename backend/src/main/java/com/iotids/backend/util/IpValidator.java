package com.iotids.backend.util;

import java.util.regex.Pattern;

public class IpValidator {
    private static final String IPV4_PATTERN = 
        "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}" +
        "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";

    private static final Pattern pattern = Pattern.compile(IPV4_PATTERN);

    public static boolean isValidIpv4(String ip) {
        if (ip == null) return false;
        return pattern.matcher(ip).matches();
    }
}
