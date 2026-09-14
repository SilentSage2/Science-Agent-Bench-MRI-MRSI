"""Run the frozen multi-coil MRI baseline-separation pilot."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from science_agent.research.mri_multicoil import (
    BaselineResult,
    create_multicoil_reconstruction_instance,
    evaluate_multicoil_baselines,
)

_CONFIGS = (
    ("easy", 4.0, 0.01),
    ("medium", 6.0, 0.02),
    ("hard", 8.0, 0.04),
)
_SEEDS = (1101, 1102, 1103)
_BOOTSTRAP_SEED = 20270914
_BOOTSTRAP_RESAMPLES = 10_000


def run_pilot() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for difficulty, acceleration, noise in _CONFIGS:
        for seed in _SEEDS:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_multicoil_reconstruction_instance(
                    root / "inputs",
                    root / "evaluator",
                    seed=seed,
                    matrix_size=64,
                    coils=8,
                    acceleration=acceleration,
                    relative_noise=noise,
                )
                baselines = evaluate_multicoil_baselines(root / "inputs", root / "evaluator")
            cases.append(
                {
                    "difficulty": difficulty,
                    "seed": seed,
                    "acceleration": acceleration,
                    "relative_noise": noise,
                    "baselines": {item.method: _baseline_dict(item) for item in baselines},
                }
            )

    improvements = np.asarray(
        [
            case["baselines"]["zero_filled"]["magnitude_nrmse"]
            - case["baselines"]["sense_cg"]["magnitude_nrmse"]
            for case in cases
        ],
        dtype=np.float64,
    )
    generator = np.random.default_rng(_BOOTSTRAP_SEED)
    bootstrap = np.mean(
        generator.choice(improvements, size=(_BOOTSTRAP_RESAMPLES, len(improvements))),
        axis=1,
    )
    return {
        "study": "mri-multicoil-baseline-pilot-v1",
        "research_result": False,
        "purpose": "task baseline separation and difficulty calibration",
        "matrix_size": 64,
        "coil_count": 8,
        "case_count": len(cases),
        "bootstrap_seed": _BOOTSTRAP_SEED,
        "bootstrap_resamples": _BOOTSTRAP_RESAMPLES,
        "mean_magnitude_nrmse_improvement_sense_cg_over_zero_fill": float(improvements.mean()),
        "improvement_bootstrap_95_interval": [
            float(np.quantile(bootstrap, 0.025)),
            float(np.quantile(bootstrap, 0.975)),
        ],
        "sense_cg_better_case_count": int(np.sum(improvements > 0.0)),
        "cases": cases,
    }


def _baseline_dict(result: BaselineResult) -> dict[str, float]:
    return {
        "magnitude_nrmse": result.metrics.magnitude_nrmse,
        "gradient_nrmse": result.metrics.gradient_nrmse,
        "sampled_kspace_residual": result.metrics.sampled_kspace_residual,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.output.mkdir(parents=True, exist_ok=False)
    summary = run_pilot()
    (arguments.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}))


if __name__ == "__main__":
    main()
