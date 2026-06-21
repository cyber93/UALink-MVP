"""UALink 200 — TL Field Types and Message Types (Table 5-27, 5-28)."""
from ..common.constants import TLFieldType, TL_FIELD_SECTORS


FTYPE_BITS = 4

def ftype_sectors(ftype: int) -> int:
    return TL_FIELD_SECTORS.get(ftype, 1)

def is_request_ftype(ftype: int) -> bool:
    return ftype in (TLFieldType.UNCOMPRESSED_REQ, TLFieldType.COMPRESSED_REQ)

def is_response_ftype(ftype: int) -> bool:
    return ftype in (TLFieldType.UNCOMPRESSED_RSP,
                     TLFieldType.COMPRESSED_RSP_SB,
                     TLFieldType.COMPRESSED_RSP_WR)

def is_fc_nop(ftype: int) -> bool:
    return ftype == TLFieldType.FLOW_CTRL_NOP

LEGAL_FTYPES = set(TL_FIELD_SECTORS.keys())
