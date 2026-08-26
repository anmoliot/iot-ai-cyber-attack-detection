package com.iotids.networkengine.packet;

import com.iotids.networkengine.logging.NetworkLogger;
import org.pcap4j.packet.IpV4Packet;
import org.pcap4j.packet.Packet;
import org.pcap4j.packet.TcpPacket;
import org.pcap4j.packet.UdpPacket;
import org.pcap4j.packet.IcmpV4CommonPacket;
import java.net.Inet4Address;

public class PacketParser {
    private static final NetworkLogger logger = NetworkLogger.getLogger(PacketParser.class);

    public static ParsedPacket parse(Packet packet) {
        if (packet == null) return null;

        IpV4Packet ipV4Packet = packet.get(IpV4Packet.class);
        if (ipV4Packet == null) {
            // We are only handling IPv4 for now
            return null;
        }

        Inet4Address srcAddr = ipV4Packet.getHeader().getSrcAddr();
        Inet4Address dstAddr = ipV4Packet.getHeader().getDstAddr();
        
        String srcIp = srcAddr.getHostAddress();
        String dstIp = dstAddr.getHostAddress();
        int length = packet.length();
        // Fallback to System.currentTimeMillis if packet timestamp isn't directly available from Pcap4J Packet interface
        long timestamp = System.currentTimeMillis(); 

        ProtocolType protocol = ProtocolType.UNKNOWN;

        if (packet.contains(TcpPacket.class)) {
            protocol = ProtocolType.TCP;
        } else if (packet.contains(UdpPacket.class)) {
            protocol = ProtocolType.UDP;
        } else if (packet.contains(IcmpV4CommonPacket.class)) {
            protocol = ProtocolType.ICMP;
        }

        return new ParsedPacket(srcIp, dstIp, protocol, length, timestamp);
    }
}
