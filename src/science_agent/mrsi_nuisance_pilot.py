"""Run the frozen complex-MRSI baseline-separation pilot."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from science_agent.research.mrsi_nuisance import (
    MRSIBaselineResult,
    create_complex_mrsi_instance,
    evaluate_complex_mrsi_baselines,
)

_DIFFICULTIES = ("easy", "moderate", "hard")
_INSTANCE_SEEDS = (2101, 2102, 2103)
_BOOTSTRAP_SEED = 20270915
_BOOTSTRAP_RESAMPLES = 10_000


def run_pilot() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for difficulty in _DIFFICULTIES:
        for replicate, seed in enumerate(_INSTANCE_SEEDS, start=1):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                create_complex_mrsi_instance(
                    root / "inputs",
                    root / "evaluator",
                    seed=seed,
                    grid_size=4,
                    spectral_points=256,
                    difficulty=difficulty,
                )
                baselines = evaluate_complex_mrsi_baselines(root / "inputs", root / "evaluator")
            cases.append(
                {
                    "instance_id": f"MRSI-{difficulty}-{replicate:02d}",
                    "difficulty": difficulty,
                    "generator_seed": seed,
                    "baselines": {item.method: _baseline_dict(item) for item in baselines},
                }
            )

    improvements = np.asarray(
        [
            case["baselines"]["fixed_projection"]["spectral_nrmse"]
            - case["baselines"]["adaptive_projection"]["spectral_nrmse"]
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
        "study": "mrsi-complex-nuisance-baseline-pilot-v1",
        "research_result": False,
        "purpose": "task baseline separation and difficulty calibration",
        "scientific_unit_warning": (
            "generator seeds and voxels are not independent biological subjects"
        ),
        "grid_size": 4,
        "spectral_points": 256,
        "case_count": len(cases),
        "bootstrap_seed": _BOOTSTRAP_SEED,
        "bootstrap_resamples": _BOOTSTRAP_RESAMPLES,
        "mean_spectral_nrmse_improvement_adaptive_over_fixed": float(improvements.mean()),
        "improvement_bootstrap_95_interval": [
            float(np.quantile(bootstrap, 0.025)),
            float(np.quantile(bootstrap, 0.975)),
        ],
        "adaptive_better_case_count": int(np.sum(improvements > 0.0)),
        "cases": cases,
    }


def _baseline_dict(result: MRSIBaselineResult) -> dict[str, float]:
    return {
        "nuisance_residual_ratio": result.metrics.nuisance_residual_ratio,
        "metabolite_retention_nrmse": result.metrics.metabolite_retention_nrmse,
        "spectral_nrmse": result.metrics.spectral_nrmse,
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
