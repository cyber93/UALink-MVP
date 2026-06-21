"""UALink 200 — Error containment and isolation mode (Section 3.4)."""
from ..common.constants import WrRspStatus
from ..upli.write_response_channel import WriteResponseChannel


class IsolationController:
    """
    Manages UPLI Originator Isolation Mode.
    ISOLATE WrRsp triggers isolation → originator stops issuing.
    Spec: Section 3.4, Fig 3-9.
    """
    def __init__(self):
        self.isolated = False

    def check_wrrsp(self, rsp: WriteResponseChannel) -> bool:
        if rsp.status == WrRspStatus.ISOLATE:
            self.isolated = True
            return True
        return False

    def reset(self):
        self.isolated = False

    def is_isolated(self) -> bool:
        return self.isolated


class DropModeController:
    """
    Drop mode: TL drops all requests/responses after link-down.
    Spec: Section 3.4, Fig 3-8.
    """
    def __init__(self):
        self.drop = False

    def enter_drop(self):
        self.drop = True

    def exit_drop(self):
        self.drop = False

    def should_drop(self) -> bool:
        return self.drop
