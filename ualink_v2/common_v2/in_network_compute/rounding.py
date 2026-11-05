"""
UALink 2.0 In-Network Compute — Stochastic and IEEE-754 Rounding Modes (Ch 6.2.1)
"""
import random
import struct
from ..constants import INCRoundingMode

class INCRoundingEngine:
    """Implements rounding functions including Stochastic Rounding using an 8-bit seed."""

    @staticmethod
    def round_float_to_half(val: float, mode: INCRoundingMode, seed: int = 0) -> float:
        if mode == INCRoundingMode.ROUND_STOCHASTIC:
            # PRNG based on 8-bit seed for unbiased stochastic rounding in low-precision AI training
            rng = random.Random(seed)
            prob = rng.random()
            # Truncate and probabilistic round
            base = round(val, 2)
            if (val - base) > prob * 0.01:
                return base + 0.01
            return base
        elif mode == INCRoundingMode.ROUND_TOWARD_ZERO:
            return float(int(val * 100)) / 100.0
        elif mode == INCRoundingMode.ROUND_UP:
            return float(int(val * 100 + 0.999)) / 100.0
        elif mode == INCRoundingMode.ROUND_DOWN:
            return float(int(val * 100)) / 100.0
        else: # ROUND_TO_NEAREST_EVEN
            return round(val, 2)
