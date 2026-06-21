class RoutingTable:
    def __init__(self):
        self.routes = {}

    def add(self, acc_id: int, port: int):
        self.routes[acc_id] = port

    def lookup(self, acc_id: int) -> int:
        return self.routes.get(acc_id, -1)
