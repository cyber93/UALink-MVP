"""UALink 200 — TL Flit packing engine (Section 5.2, Fig 5-6 to 5-32)."""
from typing import List, Tuple, Optional
from .tl_flit import TLFlit
from .field_types import ftype_sectors
from .uncompressed import UncompressedRequest, UncompressedResponse
from .compressed_request import CompressedRequest, can_compress_req
from .compressed_response import CompressedResponseSingleBeat, CompressedResponseWriteOrMulti
from .flow_control import FCNOPField
from .address_cache import AddressCache
from ..common.constants import TL_FLIT_BYTES, TLFieldType, ReqCmd


class TLFlitPacker:
    """
    Packs TL messages (requests/responses/FC) into 64B TL Flits.
    Rules:
    - Control half-flit: sectors 0-7 (32 bytes)
    - Data half-flit: sectors 8-15 (32 bytes) or second control half-flit
    - Pack messages back-to-back, FC/NOP fills remaining sectors
    - Carry-over: large payloads may span multiple flits
    Spec: Section 5.2 packing examples (Figures 5-6 through 5-32).
    """

    def __init__(self):
        self.tx_cache = AddressCache()

    def pack_requests(self, requests: List[dict]) -> List[TLFlit]:
        """Pack a list of request descriptors into TL Flits."""
        sectors: List[bytes] = []
        data_halves: List[bytes] = []

        for req in requests:
            cmd       = req.get('cmd', ReqCmd.READ)
            addr      = req.get('addr', 0)
            length    = req.get('length', 0)
            tag       = req.get('tag', 0)
            src       = req.get('src_acc_id', 0)
            dst       = req.get('dst_acc_id', 0)
            vc        = req.get('vc', 0)
            attr      = req.get('attr', 0xFF)
            metadata  = req.get('metadata', 0)
            payload   = req.get('data', b'')

            cache_idx = self.tx_cache.lookup(addr)
            if can_compress_req(cmd, addr, length, cache_idx is not None):
                if cache_idx is None:
                    cache_idx = self.tx_cache.insert(addr)
                cr = CompressedRequest(
                    src_acc_id=src, dst_acc_id=dst, tag=tag,
                    cmd=cmd, cache_index=cache_idx,
                    length=length, attr=attr, vc=vc
                )
                sectors.append(cr.serialize()[:4])
                sectors.append(cr.serialize()[4:8])
            else:
                self.tx_cache.insert(addr)
                ur = UncompressedRequest(
                    src_acc_id=src, dst_acc_id=dst, tag=tag,
                    cmd=cmd, addr=addr, length=length,
                    attr=attr, metadata=metadata, vc=vc
                )
                raw = ur.serialize()
                for i in range(4):
                    sectors.append(raw[i*4:(i+1)*4])

            if payload:
                data_halves.append(payload[:32] if len(payload) >= 32 else payload.ljust(32, b'\x00'))
                if len(payload) > 32:
                    data_halves.append(payload[32:64].ljust(32, b'\x00'))

        return self._sectors_to_flits(sectors, data_halves)

    def pack_response(self, rsp: dict) -> List[TLFlit]:
        tag     = rsp.get('tag', 0)
        status  = rsp.get('status', 0)
        vc      = rsp.get('vc', 0)
        is_wr   = rsp.get('is_write', False)
        n_beats = rsp.get('num_beats', 0)
        data    = rsp.get('data', b'')

        sectors: List[bytes] = []
        if is_wr:
            cr = CompressedResponseWriteOrMulti(tag=tag, status=status, vc=vc, is_write=True)
            sectors.append(cr.serialize())
        elif n_beats <= 1:
            cr = CompressedResponseSingleBeat(tag=tag, status=status, vc=vc)
            sectors.append(cr.serialize())
        else:
            cr = CompressedResponseWriteOrMulti(tag=tag, status=status, vc=vc, num_beats=n_beats)
            sectors.append(cr.serialize())

        data_halves = []
        if data:
            for i in range(0, len(data), 32):
                chunk = data[i:i+32].ljust(32, b'\x00')
                data_halves.append(chunk)

        return self._sectors_to_flits(sectors, data_halves)

    def _sectors_to_flits(self, sectors: List[bytes],
                           data_halves: List[bytes]) -> List[TLFlit]:
        flits: List[TLFlit] = []
        while len(sectors) < 8:
            fc = FCNOPField()
            sectors.append(fc.serialize())
        while len(sectors) > 0:
            ctrl_s = sectors[:8]
            sectors = sectors[8:]
            ctrl = b''.join(ctrl_s).ljust(32, b'\x00')
            if data_halves:
                dat = data_halves.pop(0)
            else:
                dat = bytes(32)
            flits.append(TLFlit(control_half=ctrl, data_half=dat))
        return flits
