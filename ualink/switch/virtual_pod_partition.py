class VPodPartition:
    def __init__(self, vpod_id: int):
        self.vpod_id = vpod_id
        self.ports = set()
