class SwitchPort:
    def __init__(self, idx: int):
        self.idx = idx
        self.connected = False
        self.peer = None
