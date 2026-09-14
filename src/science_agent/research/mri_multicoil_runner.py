"""Container entry point for one allowlisted multi-coil reconstruction candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from science_agent.research.mri_multicoil import run_multicoil_reconstruction


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("zero_filled", "sense_cg"), required=True)
    parser.add_argument("--regularization", type=float)
    parser.add_argument("--iterations", type=int)
    arguments = parser.parse_args()
    run_multicoil_reconstruction(
        Path("/inputs"),
        Path("/outputs"),
        method=arguments.method,
        regularization=arguments.regularization,
        iterations=arguments.iterations,
    )


if __name__ == "__main__":
    main()
