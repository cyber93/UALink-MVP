from ..common.constants import SecurityStream
from .key_derivation import derive_key, make_context

class KeyManager:
    def __init__(self, src: int, dst: int):
        self.src = src
        self.dst = dst
        self.master_active = b''
        self.master_alt = b''
        self.derived = {s: b'' for s in SecurityStream}
        self.epochs = {s: 0 for s in SecurityStream}

    def set_master(self, key: bytes, is_active: bool=True):
        if is_active: self.master_active = key
        else: self.master_alt = key

    def update_derived(self, stream: SecurityStream):
        self.epochs[stream] += 1
        ctx = make_context(self.src, self.dst, stream, self.epochs[stream])
        self.derived[stream] = derive_key(self.master_active, ctx)

    def get_key(self, stream: SecurityStream) -> bytes:
        return self.derived[stream]
