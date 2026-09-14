"""Container entry point for one allowlisted complex-MRSI nuisance candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from science_agent.research.mrsi_nuisance import run_complex_mrsi_nuisance_removal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--method", choices=("fixed_projection", "adaptive_projection"), required=True
    )
    parser.add_argument("--shift-steps", type=int)
    arguments = parser.parse_args()
    run_complex_mrsi_nuisance_removal(
        Path("/inputs"),
        Path("/outputs"),
        method=arguments.method,
        shift_steps=arguments.shift_steps,
    )


if __name__ == "__main__":
    main()
