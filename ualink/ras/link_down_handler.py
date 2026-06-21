"""UALink 200 — Link-down error handling flow (Section 3.4, Fig 3-7 to 3-11)."""
from .error_types import RASEvent, LinkDownError, RASErrorLog
from .error_containment import DropModeController, IsolationController


class LinkDownHandler:
    """
    Orchestrates recovery on link-down error:
    1. PHY detects link down
    2. DL enters DL_IDLE
    3. TL enters drop mode
    4. Accelerator UPLI Originator enters isolation
    5. Other Accelerators time out pending transactions
    6. Software fault management completes recovery
    """
    def __init__(self, acc_id: int, port_id: int, log: RASErrorLog):
        self.acc_id   = acc_id
        self.port_id  = port_id
        self.log      = log
        self.drop_ctl = DropModeController()
        self.iso_ctl  = IsolationController()
        self.link_up  = True

    def on_link_down(self):
        self.link_up = False
        self.drop_ctl.enter_drop()
        self.log.log(RASEvent(
            error_type=LinkDownError.LINK_DOWN,
            port_id=self.port_id,
            acc_id=self.acc_id,
            detail="Link down detected",
            recoverable=True
        ))

    def on_link_up(self):
        self.link_up = True
        self.drop_ctl.exit_drop()
        self.iso_ctl.reset()

    def is_dropping(self) -> bool:
        return self.drop_ctl.should_drop()
