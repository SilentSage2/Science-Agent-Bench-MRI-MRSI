"""Design-stage sensitivity calculations for paired binary validity outcomes."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from statistics import NormalDist


@dataclass(frozen=True, slots=True)
class PairedSensitivity:
    absolute_effect: float
    discordant_probability: float
    alpha: float
    power: float
    required_instances: int


def required_paired_instances(
    *,
    absolute_effect: float,
    discordant_probability: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> PairedSensitivity:
    """Approximate paired-instance n for a two-sided difference in binary outcomes.

    The variance term follows the paired difference of two Bernoulli outcomes.
    This is a design sensitivity calculation, not a substitute for the frozen
    exact/clustered analysis or a claim that its assumptions are true.
    """
    if not 0.0 < absolute_effect < 1.0:
        raise ValueError("absolute_effect must be in (0, 1)")
    if not absolute_effect <= discordant_probability <= 1.0:
        raise ValueError("discordant_probability must be in [absolute_effect, 1]")
    if not 0.0 < alpha < 1.0 or not 0.0 < power < 1.0:
        raise ValueError("alpha and power must be in (0, 1)")
    normal = NormalDist()
    z_alpha = normal.inv_cdf(1.0 - alpha / 2.0)
    z_power = normal.inv_cdf(power)
    variance = discordant_probability - absolute_effect**2
    required = math.ceil((z_alpha + z_power) ** 2 * variance / absolute_effect**2)
    return PairedSensitivity(
        absolute_effect=absolute_effect,
        discordant_probability=discordant_probability,
        alpha=alpha,
        power=power,
        required_instances=required,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--power", type=float, default=0.80)
    arguments = parser.parse_args()
    print("discordance effect required_paired_instances")
    for discordance in (0.25, 0.35, 0.50):
        for effect in (0.10, 0.15, 0.20):
            result = required_paired_instances(
                absolute_effect=effect,
                discordant_probability=discordance,
                alpha=arguments.alpha,
                power=arguments.power,
            )
            print(f"{discordance:.2f} {effect:.2f} {result.required_instances}")


if __name__ == "__main__":
    main()
