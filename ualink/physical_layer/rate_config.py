"""UALink 200 — Rate and link width configurations (Section 7.1, Table 7-1, 7-2)."""
from dataclasses import dataclass
from ..common.constants import SerialRate, LinkWidth, AM_INTERVAL_FLITS


@dataclass
class RateConfig:
    rate: SerialRate
    width: LinkWidth
    flit_time_ns: float  # nanoseconds per 640B DL Flit
    am_interval: int     # alignment marker interval in flits
    fec_interleave: int  # 1, 2, or 4
    clauses: list        # 802.3 clause references


RATE_CONFIGS = {
    (SerialRate.G100, LinkWidth.X1): RateConfig(
        rate=SerialRate.G100, width=LinkWidth.X1,
        flit_time_ns=25.6, am_interval=4096,
        fec_interleave=4, clauses=[82, 91]
    ),
    (SerialRate.G200, LinkWidth.X1): RateConfig(
        rate=SerialRate.G200, width=LinkWidth.X1,
        flit_time_ns=25.0, am_interval=4096,
        fec_interleave=4, clauses=[117, 119, 176]
    ),
    (SerialRate.G400, LinkWidth.X2): RateConfig(
        rate=SerialRate.G400, width=LinkWidth.X2,
        flit_time_ns=12.5, am_interval=8192,
        fec_interleave=4, clauses=[117, 119, 176]
    ),
    (SerialRate.G800, LinkWidth.X4): RateConfig(
        rate=SerialRate.G800, width=LinkWidth.X4,
        flit_time_ns=6.25, am_interval=16384,
        fec_interleave=4, clauses=[170, 172]
    ),
}


def get_config(rate: SerialRate, width: LinkWidth) -> RateConfig:
    cfg = RATE_CONFIGS.get((rate, width))
    if cfg is None:
        raise ValueError(f"Unsupported rate/width: {rate.name}/{width.name}")
    return cfg

def get_ack_timeout_flits(rtt_ns: float, rate: SerialRate,
                           width: LinkWidth) -> int:
    cfg = get_config(rate, width)
    return max(1, int(rtt_ns / cfg.flit_time_ns))
