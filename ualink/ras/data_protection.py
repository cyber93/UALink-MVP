"""UALink 200 — End-to-end data protection (Section 3.3)."""
from ..common.parity import even_parity, compute_data_parity


POISON_PATTERN = bytes([0xFF] * 64)


def check_req_parity(req) -> bool:
    vld_ok  = even_parity(int(req.valid), 1) == req.vld_parity
    addr_ok = even_parity(req.addr, 57) == req.addr_parity
    return vld_ok and addr_ok

def check_rdrsp_parity(rsp) -> bool:
    vld_ok  = even_parity(int(rsp.valid), 1) == rsp.vld_parity
    dp_ok   = compute_data_parity(rsp.data) == rsp.data_parity
    return vld_ok and dp_ok

def poison_data_beat(beat) -> None:
    beat.data = POISON_PATTERN
    beat.data_error = True

def is_poisoned(beat) -> bool:
    return beat.data_error

def manufactured_data() -> bytes:
    return POISON_PATTERN
