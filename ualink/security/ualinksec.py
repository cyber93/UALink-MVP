from .key_manager import KeyManager
from .iv_manager import IVManager

class UALinkSec:
    def __init__(self, src: int, dst: int):
        self.km = KeyManager(src, dst)
        self.ivm = IVManager(src, dst)
