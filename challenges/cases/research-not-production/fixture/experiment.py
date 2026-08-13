from __future__ import annotations

import math
import random


def baseline(x: float) -> float:
    return abs(x)


def proposed(x: float) -> float:
    return math.sqrt(x * x + 0.25) - 0.5


def run(seed: int = 7, samples: int = 1000) -> dict[str, float]:
    rng = random.Random(seed)
    values = [rng.uniform(-5.0, 5.0) for _ in range(samples)]
    baseline_mean = sum(baseline(value) for value in values) / samples
    proposed_mean = sum(proposed(value) for value in values) / samples
    return {
        "baseline_mean": baseline_mean,
        "proposed_mean": proposed_mean,
        "improvement": baseline_mean - proposed_mean,
    }


if __name__ == "__main__":
    print(run())
