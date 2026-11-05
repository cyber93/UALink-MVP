"""
UALink Manageability Specification v1.0 — Enterprise Telemetry & Health Monitoring
Tracks fine-grained link BER, flit throughput, and collective acceleration latency.
"""
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class PortTelemetryMetrics:
    port_id: int
    flits_tx: int = 0
    flits_rx: int = 0
    crc_errors: int = 0
    replay_events: int = 0
    inc_reductions_completed: int = 0

class EnterpriseTelemetryCollector:
    """Centralized telemetry aggregator across all accelerators and switches in a Pod."""
    def __init__(self):
        self.metrics: Dict[int, PortTelemetryMetrics] = {}

    def get_port_metrics(self, port_id: int) -> PortTelemetryMetrics:
        if port_id not in self.metrics:
            self.metrics[port_id] = PortTelemetryMetrics(port_id=port_id)
        return self.metrics[port_id]

    def record_tx(self, port_id: int, count: int = 1):
        self.get_port_metrics(port_id).flits_tx += count

    def record_rx(self, port_id: int, count: int = 1):
        self.get_port_metrics(port_id).flits_rx += count

    def record_crc_error(self, port_id: int):
        self.get_port_metrics(port_id).crc_errors += 1
