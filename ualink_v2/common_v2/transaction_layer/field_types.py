"""
UALink 2.0 Common Specification — Transaction Layer Field Types (Table 5-27)
"""
from enum import IntEnum

class TLFieldType(IntEnum):
    FLOW_CTRL_NOP       = 0x0   # 1 sector
    UNCOMPRESSED_RSP    = 0x2   # 2 sectors
    UNCOMPRESSED_REQ    = 0x4   # 4 sectors
    COMPRESSED_REQ      = 0x6   # 2 sectors
    COMPRESSED_RSP_SB   = 0x8   # 1 sector (single-beat read response)
    COMPRESSED_RSP_WR   = 0x9   # 1 sector (write or multi-beat read response)

TL_FIELD_SECTORS = {
    TLFieldType.FLOW_CTRL_NOP:     1,
    TLFieldType.UNCOMPRESSED_RSP:  2,
    TLFieldType.UNCOMPRESSED_REQ:  4,
    TLFieldType.COMPRESSED_REQ:    2,
    TLFieldType.COMPRESSED_RSP_SB: 1,
    TLFieldType.COMPRESSED_RSP_WR: 1,
}
