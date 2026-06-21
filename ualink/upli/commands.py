"""UALink 200 — UPLI Commands: encodings, validation, beat counts."""
from ..common.constants import ReqCmd, UPLIWriteMsgType, AtomicOpSize, is_write_class, is_vdc

READ_CMDS  = {ReqCmd.READ}
READ_VDC   = set(range(0x08, 0x10))
WRITE_CMDS = {ReqCmd.WRITE, ReqCmd.WRITE_FULL, ReqCmd.UPLI_WRITE_MSG}
WRITE_VDC  = set(range(0x2C, 0x30))
ATOM_CMDS  = {ReqCmd.ATOMIC_R, ReqCmd.ATOMIC_NR}
ATOM_VDC   = set(range(0x3C, 0x40))

USES_RDRSP_CHAN = READ_CMDS | READ_VDC | {ReqCmd.ATOMIC_R}
USES_WRRSP_CHAN = WRITE_CMDS | WRITE_VDC | {ReqCmd.ATOMIC_NR}


def uses_orig_data(cmd: int) -> bool:
    return bool(cmd & 0x20)

def response_channel(cmd: int, msg_type: int = 0) -> str:
    if cmd == ReqCmd.UPLI_WRITE_MSG:
        if msg_type == UPLIWriteMsgType.KEY_ROLL_RDRSP_CHANNEL:
            return 'read'
        return 'write'
    if cmd in USES_RDRSP_CHAN or cmd in READ_VDC:
        return 'read'
    return 'write'

def validate_read(addr: int, length_dw: int) -> None:
    assert (addr & 0x3) == 0, "Read addr must be DW-aligned"
    assert 0 <= length_dw <= 63, f"ReqLen {length_dw} out of range"
    size = (length_dw + 1) * 4
    assert size <= 256, f"Read size {size} exceeds 256B"
    end = addr + size - 1
    assert (addr & ~0xFF) == (end & ~0xFF), "Read crosses 256B boundary"

def validate_write(addr: int, length_dw: int, full: bool = False) -> None:
    assert (addr & 0x3) == 0, "Write addr must be DW-aligned"
    size = (length_dw + 1) * 4
    assert size <= 256, f"Write size {size} exceeds 256B"
    end = addr + size - 1
    assert (addr & ~0xFF) == (end & ~0xFF), "Write crosses 256B boundary"
    if full:
        assert (addr & 0x3F) == 0, "WriteFull must start on 64B boundary"
        assert size in (64, 128, 192, 256), "WriteFull size must be 64/128/192/256"

def validate_atomic_single(addr: int, length_dw: int, op_size: int) -> None:
    elem_bytes = [4, 8, 2, 1][op_size]
    assert (addr % elem_bytes) == 0, "Atomic addr must be element-aligned"
    size = (length_dw + 1) * 4
    assert size % elem_bytes == 0
    assert size <= 64, "Single-operand atomic must fit in 1 beat (64B)"
    end = addr + size - 1
    assert (addr & ~0x3F) == (end & ~0x3F), "Single atomic crosses 64B boundary"

def num_beats(cmd: int, length_dw: int) -> int:
    size = (length_dw + 1) * 4
    return (size + 63) // 64

def encode_req_attr_read(first_dw_be: int, last_dw_be: int) -> int:
    return ((last_dw_be & 0xF) << 4) | (first_dw_be & 0xF)

def decode_req_attr_read(attr: int):
    return (attr & 0xF), ((attr >> 4) & 0xF)

def encode_req_attr_atomic(op_type: int, op_size: int) -> int:
    return ((op_type & 0x1E) << 3) | ((op_size & 0x3) << 2) | (op_type & 0x1)
