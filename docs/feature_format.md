# Feature Format

The feature builder reads `models/features.json` and produces one ordered vector per flow.

Example:

```json
[
  "duration",
  "protocol",
  "src_port",
  "dst_port",
  "packet_count",
  "byte_count",
  "avg_packet_size"
]
```

## Current Supported Flow Features

- `duration`
- `protocol`
- `src_port`
- `dst_port`
- `packet_count`
- `byte_count`
- `avg_packet_size`
- `src_bytes`
- `dst_bytes`
- `tcp_count`
- `udp_count`
- `icmp_count`

Unsupported features are filled with `0.0` by default and should be reviewed before final training/evaluation.

## Protocol Encoding

The current simple encoding is:

```text
TCP  -> 6
UDP  -> 17
ICMP -> 1
Other -> 0
```

Use the same encoding during training and inference.
