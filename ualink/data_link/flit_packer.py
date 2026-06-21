"""UALink 200 — TL→DL Flit packing (Section 6.2, Fig 6-5)."""
from typing import List
from .dl_flit import DLFlit, FlitHeader
from .segment import DLSegment, SEG_PAYLOAD_BYTES
from ..transaction_layer.tl_flit import TLFlit
from ..common.constants import DL_SEGMENT_COUNT


class DLFlitPacker:
    """
    Packs 64B TL Flits into 640B DL Flits.
    TL Flits are placed sector-by-sector into DL segments.
    Carry-over: TL Flit payload may span segment boundary.
    NOP DL Flit = DL Flit where all TL content is NOP (op=0, no payload).
    Spec: Section 6.2 packing rules, Fig 6-5.
    """

    def __init__(self):
        self._carry: bytes = b''  # carry-over bytes from prev TL flit

    def pack(self, tl_flits: List[TLFlit], seq_no: int = 1,
             op: int = 0, ack_req_seq: int = 0) -> DLFlit:
        """Pack TL Flits into one 640B DL Flit."""
        dl = DLFlit()
        dl.flit_header = FlitHeader(op=op, ack_req_seq=ack_req_seq,
                                     flit_seq_lo=seq_no & 0x7)
        payload = self._carry
        for tf in tl_flits:
            payload += tf.to_bytes()
        self._carry = b''

        total_cap = sum(SEG_PAYLOAD_BYTES)
        if len(payload) > total_cap:
            self._carry = payload[total_cap:]
            payload = payload[:total_cap]

        dl.set_payload(payload)
        dl.compute_crc()
        return dl

    def make_nop_flit(self, seq_no: int = 0,
                      ack_req_seq: int = 0, op: int = 0) -> DLFlit:
        dl = DLFlit()
        dl.flit_header = FlitHeader(op=op, ack_req_seq=ack_req_seq,
                                     flit_seq_lo=seq_no & 0x7)
        dl.compute_crc()
        return dl

    def unpack(self, dl_flit: DLFlit) -> bytes:
        """Extract raw TL payload bytes from DL Flit."""
        return dl_flit.get_payload_bytes()
