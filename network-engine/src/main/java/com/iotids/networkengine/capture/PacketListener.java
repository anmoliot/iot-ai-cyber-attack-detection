package com.iotids.networkengine.capture;

import org.pcap4j.packet.Packet;

public interface PacketListener {
    void onPacket(Packet packet);
}
