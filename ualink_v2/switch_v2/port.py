"""
UALink 2.0 Switch — Port Model and Bifurcation (Chapter 10)
"""
class SwitchPort2:
    def __init__(self, port_idx: int, width_lanes: int = 4):
        self.idx = port_idx
        self.width_lanes = width_lanes  # x1, x2, x4 bifurcation
        self.enabled = True
        self.flits_forwarded = 0

    def bifurcate(self, target_width: int):
        assert target_width in (1, 2, 4)
        self.width_lanes = target_width
