"""UALink 200 — DL Messages (Section 6.3, Table 6-3)."""
from dataclasses import dataclass
from ..common.constants import DLMsgType, DLAckField


DL_MSG_SIGNATURE = 0xA5  # DL message start byte

@dataclass
class DLMessage:
    msg_class: int = 0
    msg_type: int = 0
    payload: bytes = b''

    def to_bytes(self) -> bytes:
        header = bytes([DL_MSG_SIGNATURE, (self.msg_class & 0x3) | (self.msg_type << 2)])
        return header + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> 'DLMessage':
        obj = cls()
        obj.msg_class = data[1] & 0x3
        obj.msg_type  = (data[1] >> 2) & 0x3F
        obj.payload   = data[2:]
        return obj


def make_tl_rate_notification(rate_gbps: int) -> DLMessage:
    return DLMessage(msg_class=0, msg_type=DLMsgType.TL_RATE_NOTIFICATION,
                     payload=bytes([rate_gbps & 0xFF]))

def make_device_id_req() -> DLMessage:
    return DLMessage(msg_class=0, msg_type=DLMsgType.DEVICE_ID_REQUEST)

def make_port_id_req() -> DLMessage:
    return DLMessage(msg_class=0, msg_type=DLMsgType.PORT_ID_REQUEST)

def make_nop_msg() -> DLMessage:
    return DLMessage(msg_class=0, msg_type=DLMsgType.NO_OP)

def make_channel_neg(ack_field: int = DLAckField.REQUEST,
                     max_flits: int = 512) -> DLMessage:
    payload = bytes([ack_field & 0x3, (max_flits >> 8) & 0xFF, max_flits & 0xFF])
    return DLMessage(msg_class=1, msg_type=DLMsgType.CHANNEL_NEGOTIATION, payload=payload)
