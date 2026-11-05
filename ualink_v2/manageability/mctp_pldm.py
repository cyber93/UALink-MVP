"""
UALink Manageability Specification v1.0 — MCTP / PLDM Enterprise Protocol Binding
Specifies out-of-band management binding over PCIe/I2C/SMBus/UART.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class MCTPPacketHeader:
    header_version: int = 1
    destination_eid: int = 0
    source_eid: int = 0
    message_tag: int = 0
    packet_sequence: int = 0

class PLDMMessageAgent:
    """Simulates PLDM monitoring messages (Type 0x02: Monitoring & Control)."""
    def __init__(self, eid: int):
        self.eid = eid

    def format_sensor_reading_request(self, sensor_id: int) -> bytes:
        return bytes([0x80, 0x02, 0x11, sensor_id & 0xFF, (sensor_id >> 8) & 0xFF])

    def format_sensor_reading_response(self, sensor_id: int, reading_val: int) -> bytes:
        # PLDM success completion code (0x00) + sensor reading
        return bytes([0x00, 0x02, 0x11, 0x00]) + reading_val.to_bytes(4, 'little')
