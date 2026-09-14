from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from science_agent.paired_analysis import AnalysisError, analyze_records, write_figure_data


def _record(family: str, instance: str, condition: str, valid: bool) -> dict[str, object]:
    return {
        "family": family,
        "instance_id": instance,
        "condition": condition,
        "repetition": 0,
        "technically_completed": True,
        "scientifically_valid": valid,
        "invalidity_detected": not valid and condition == "plan_retry_replan",
        "eligible_denominator": True,
        "exclusion_code": None,
        "provider_input_tokens": 10,
        "provider_output_tokens": 5,
        "estimated_cost_microusd": 80,
        "wall_time_ms": 12,
        "tool_calls": 1,
        "retries": 0,
    }


def test_family_stratified_pairing_bootstrap_and_exact_randomization() -> None:
    records: list[dict[str, object]] = []
    for family in ("mri_multicoil", "mrsi_nuisance"):
        for index in range(4):
            instance = f"{family}-{index}"
            records.append(_record(family, instance, "reactive", False))
            records.append(_record(family, instance, "plan_retry_replan", index < 3))
    analysis = analyze_records(records, resamples=500, bootstrap_seed=7)

    validity = [
        item for item in analysis["estimates"] if item["endpoint"] == "scientifically_valid"
    ]
    assert len(validity) == 2
    assert all(item["paired_instance_count"] == 4 for item in validity)
    assert all(item["estimate"] == 0.75 for item in validity)
    assert all(item["exact_sign_flip_pvalue"] == 0.25 for item in validity)
    assert analysis["exclusion_counts"] == {}


def test_missingness_is_reported_and_incomplete_pairs_are_not_imputed() -> None:
    records = [
        _record("mri_multicoil", "one", "reactive", False),
        _record("mri_multicoil", "one", "plan_retry_replan", True),
        _record("mri_multicoil", "two", "reactive", False),
        _record("mri_multicoil", "two", "plan_retry_replan", True),
    ]
    records[-1]["exclusion_code"] = "provider_failure"
    records[-1]["eligible_denominator"] = False
    analysis = analyze_records(records, resamples=50)
    estimate = next(
        item for item in analysis["estimates"] if item["endpoint"] == "scientifically_valid"
    )

    assert estimate["paired_instance_count"] == 1
    assert analysis["exclusion_counts"] == {"provider_failure": 1}


def test_figure_pipeline_marks_development_data_ineligible() -> None:
    records = [
        _record("mri_multicoil", "one", "reactive", False),
        _record("mri_multicoil", "one", "plan_retry_replan", True),
    ]
    analysis = analyze_records(records, resamples=20)
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "figures"
        write_figure_data(
            records,
            analysis,
            output,
            data_status="development_model_checkout",
            source_revision="abc",
        )
        figure = json.loads((output / "figure_3_agent_endpoints.json").read_text())

    assert figure["result_figure_eligible"] is False
    assert figure["data_status"] == "development_model_checkout"


def test_duplicate_record_key_fails_closed() -> None:
    record = _record("mri_multicoil", "one", "reactive", False)
    with pytest.raises(AnalysisError, match="unique"):
        analyze_records([record, dict(record)], resamples=10)
