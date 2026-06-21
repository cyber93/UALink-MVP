"""UALink 200 — RAS Error Types (Section 3.2)."""
from enum import IntEnum, auto
from dataclasses import dataclass


class UPLIErrorType(IntEnum):
    CONTROL_ERROR   = auto()  # Parity on *Vld, control fields, credit return
    DATA_ERROR      = auto()  # Parity on data fields → poison
    PROTOCOL_ERROR  = auto()  # Protocol rule violation

class SwitchErrorType(IntEnum):
    CORE_CONTROL    = auto()
    CORE_DATA       = auto()

class LinkDownError(IntEnum):
    LINK_DOWN       = auto()  # UALink link became inoperable


@dataclass
class RASEvent:
    error_type: object  # UPLIErrorType | SwitchErrorType | LinkDownError
    port_id: int
    acc_id: int
    detail: str = ""
    recoverable: bool = True


class RASErrorLog:
    def __init__(self):
        self._events = []

    def log(self, event: RASEvent):
        self._events.append(event)

    def get_all(self):
        return list(self._events)

    def clear(self):
        self._events.clear()

    def has_link_down(self) -> bool:
        return any(isinstance(e.error_type, LinkDownError) for e in self._events)
