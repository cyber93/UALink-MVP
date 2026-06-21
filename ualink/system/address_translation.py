"""UALink 200 — Address Translation Model (Section 1.5)."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PageTableEntry:
    address_handle: int
    peer_acc_id: int
    is_npa: bool = True  # True=NPA, False=SPA


class MMU:
    """Accelerator MMU: GVA → NPA (cross-domain) or SPA (local)."""
    def __init__(self):
        self._table: Dict[int, PageTableEntry] = {}

    def map(self, gva: int, entry: PageTableEntry):
        self._table[gva] = entry

    def translate(self, gva: int) -> Optional[PageTableEntry]:
        return self._table.get(gva)


class LinkMMU:
    """Link MMU: NPA → local SPA at destination accelerator."""
    def __init__(self):
        self._table: Dict[int, int] = {}  # address_handle → local_spa

    def register(self, address_handle: int, local_spa: int):
        self._table[address_handle] = local_spa

    def translate(self, address_handle: int) -> Optional[int]:
        return self._table.get(address_handle)


class AddressTranslator:
    """Full cross-domain translation: GVA → NPA → SPA."""
    def __init__(self):
        self.mmu = MMU()
        self.link_mmu = LinkMMU()

    def resolve(self, gva: int) -> tuple:
        """Returns (is_npa, acc_id_or_none, physical_addr)."""
        pte = self.mmu.translate(gva)
        if pte is None:
            return False, None, gva
        if pte.is_npa:
            spa = self.link_mmu.translate(pte.address_handle)
            return True, pte.peer_acc_id, spa
        return False, None, pte.address_handle
