"""
UALink 2.0 Address Translation Model (GVA -> NPA -> SPA)
Spec: Section 1.5
"""
from typing import Dict, Tuple

class AddressTranslationModel:
    """Simulates 3-stage cross-domain address translation."""
    def __init__(self):
        self.gva_to_npa: Dict[int, int] = {} # GVA page -> NPA page
        self.npa_to_spa: Dict[Tuple[int, int], int] = {} # (AccID, NPA page) -> SPA page

    def map_page(self, acc_id: int, gva: int, spa: int, page_size: int = 4096):
        gva_page = gva // page_size
        spa_page = spa // page_size
        npa_page = gva_page + 0x1000
        self.gva_to_npa[gva_page] = npa_page
        self.npa_to_spa[(acc_id, npa_page)] = spa_page

    def translate_gva_to_spa(self, acc_id: int, gva: int, page_size: int = 4096) -> int:
        offset = gva % page_size
        gva_page = gva // page_size
        npa_page = self.gva_to_npa.get(gva_page, gva_page)
        spa_page = self.npa_to_spa.get((acc_id, npa_page), npa_page)
        return (spa_page * page_size) + offset
