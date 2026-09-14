"""Paired family-stratified analysis and figure-data export for agent outcomes."""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

ENDPOINTS = ("scientifically_valid", "invalidity_detected")


class AnalysisError(ValueError):
    """Raised when paired analysis inputs are incomplete or ambiguous."""


def analyze_records(
    records: list[dict[str, Any]],
    *,
    intervention: str = "plan_retry_replan",
    comparator: str = "reactive",
    bootstrap_seed: int = 2701,
    resamples: int = 10_000,
) -> dict[str, Any]:
    if resamples <= 0:
        raise AnalysisError("resamples must be positive")
    normalized = [_validate_record(record) for record in records]
    duplicates = Counter(
        (row["family"], row["instance_id"], row["condition"], row["repetition"])
        for row in normalized
    )
    if any(count != 1 for count in duplicates.values()):
        raise AnalysisError("family/instance/condition/repetition keys must be unique")
    estimates: list[dict[str, Any]] = []
    for family in sorted({row["family"] for row in normalized}):
        family_rows = [row for row in normalized if row["family"] == family]
        for endpoint in ENDPOINTS:
            paired = _paired_instance_differences(family_rows, intervention, comparator, endpoint)
            if not paired:
                continue
            differences = [value for _, value in paired]
            interval = _cluster_bootstrap_interval(
                differences, seed=bootstrap_seed, resamples=resamples
            )
            estimates.append(
                {
                    "family": family,
                    "endpoint": endpoint,
                    "intervention": intervention,
                    "comparator": comparator,
                    "paired_instance_count": len(paired),
                    "estimate": sum(differences) / len(differences),
                    "interval_95": interval,
                    "exact_sign_flip_pvalue": _exact_sign_flip_pvalue(differences),
                    "instance_differences": [
                        {"instance_id": instance, "difference": difference}
                        for instance, difference in paired
                    ],
                }
            )
    exclusions = Counter(
        str(row["exclusion_code"]) for row in normalized if row["exclusion_code"] is not None
    )
    condition_counts: dict[str, dict[str, int]] = {}
    for condition in sorted({row["condition"] for row in normalized}):
        members = [row for row in normalized if row["condition"] == condition]
        condition_counts[condition] = {
            "records": len(members),
            "technically_completed": sum(row["technically_completed"] for row in members),
            "scientifically_valid": sum(row["scientifically_valid"] for row in members),
            "invalidity_detected": sum(row["invalidity_detected"] for row in members),
            "excluded": sum(row["exclusion_code"] is not None for row in members),
        }
    return {
        "analysis_schema": "paired-family-cluster-v1",
        "unit": "independent task instance; repetitions averaged within instance",
        "intervention": intervention,
        "comparator": comparator,
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_resamples": resamples,
        "estimates": estimates,
        "condition_denominators": condition_counts,
        "exclusion_counts": dict(sorted(exclusions.items())),
        "record_count": len(normalized),
    }


def write_figure_data(
    records: list[dict[str, Any]],
    analysis: dict[str, Any],
    output: Path,
    *,
    data_status: str,
    source_revision: str,
) -> None:
    allowed = {
        "development_model_checkout",
        "frozen_real_model_result",
    }
    if data_status not in allowed:
        raise AnalysisError(f"unsupported data status: {data_status}")
    output.mkdir(parents=True, exist_ok=False)
    result_eligible = data_status == "frozen_real_model_result"
    common = {
        "source_revision": source_revision,
        "data_status": data_status,
        "result_figure_eligible": result_eligible,
        "analysis_schema": analysis["analysis_schema"],
    }
    figure3 = {
        **common,
        "figure_id": "figure_3_agent_endpoints",
        "analysis_command": "sab-analyze-paired --input INPUT --output OUTPUT",
        "records": [
            {
                key: row[key]
                for key in (
                    "family",
                    "condition",
                    "instance_id",
                    "repetition",
                    "technically_completed",
                    "scientifically_valid",
                    "invalidity_detected",
                    "eligible_denominator",
                    "exclusion_code",
                )
            }
            for row in records
        ],
        "estimates": analysis["estimates"],
    }
    figure4 = {
        **common,
        "figure_id": "figure_4_efficiency",
        "analysis_command": "sab-analyze-paired --input INPUT --output OUTPUT",
        "records": [
            {
                key: row[key]
                for key in (
                    "family",
                    "condition",
                    "instance_id",
                    "repetition",
                    "provider_input_tokens",
                    "provider_output_tokens",
                    "estimated_cost_microusd",
                    "wall_time_ms",
                    "tool_calls",
                    "retries",
                )
            }
            for row in records
        ],
    }
    for name, payload in (
        ("analysis_summary.json", analysis),
        ("figure_3_agent_endpoints.json", figure3),
        ("figure_4_efficiency.json", figure4),
    ):
        (output / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def _validate_record(record: dict[str, Any]) -> dict[str, Any]:
    required = {
        "family",
        "instance_id",
        "condition",
        "repetition",
        "technically_completed",
        "scientifically_valid",
        "invalidity_detected",
        "eligible_denominator",
        "exclusion_code",
        "provider_input_tokens",
        "provider_output_tokens",
        "estimated_cost_microusd",
        "wall_time_ms",
        "tool_calls",
        "retries",
    }
    missing = required.difference(record)
    if missing:
        raise AnalysisError(f"record missing fields: {sorted(missing)}")
    row = dict(record)
    for key in (
        "technically_completed",
        "scientifically_valid",
        "invalidity_detected",
        "eligible_denominator",
    ):
        if not isinstance(row[key], bool):
            raise AnalysisError(f"{key} must be boolean")
    if row["invalidity_detected"] and row["scientifically_valid"]:
        raise AnalysisError("a valid result cannot be an invalidity detection")
    return row


def _paired_instance_differences(
    rows: list[dict[str, Any]], intervention: str, comparator: str, endpoint: str
) -> list[tuple[str, float]]:
    values: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in rows:
        if row["condition"] not in {intervention, comparator}:
            continue
        if row["exclusion_code"] is not None or not row["eligible_denominator"]:
            continue
        if endpoint == "invalidity_detected" and row["scientifically_valid"]:
            continue
        values[(row["instance_id"], row["condition"])].append(bool(row[endpoint]))
    differences: list[tuple[str, float]] = []
    instance_ids = sorted({key[0] for key in values})
    for instance_id in instance_ids:
        intervention_values = values.get((instance_id, intervention), [])
        comparator_values = values.get((instance_id, comparator), [])
        if not intervention_values or not comparator_values:
            continue
        intervention_mean = sum(intervention_values) / len(intervention_values)
        comparator_mean = sum(comparator_values) / len(comparator_values)
        differences.append((instance_id, intervention_mean - comparator_mean))
    return differences


def _cluster_bootstrap_interval(
    differences: list[float], *, seed: int, resamples: int
) -> list[float]:
    generator = random.Random(seed)
    size = len(differences)
    samples = sorted(
        sum(generator.choice(differences) for _ in range(size)) / size for _ in range(resamples)
    )
    return [_quantile(samples, 0.025), _quantile(samples, 0.975)]


def _quantile(values: list[float], probability: float) -> float:
    position = probability * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def _exact_sign_flip_pvalue(differences: list[float]) -> float:
    fractions = [Fraction(str(value)) for value in differences if value != 0.0]
    if not fractions:
        return 1.0
    distribution: dict[Fraction, int] = {Fraction(0): 1}
    for value in fractions:
        updated: dict[Fraction, int] = defaultdict(int)
        for total, count in distribution.items():
            updated[total + value] += count
            updated[total - value] += count
        distribution = dict(updated)
    observed = abs(sum(fractions, Fraction(0)))
    extreme = 0
    for total, count in distribution.items():
        if abs(total) >= observed:
            extreme += count
    return float(extreme / (2 ** len(fractions)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data-status", default="development_model_checkout")
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--bootstrap-seed", type=int, default=2701)
    parser.add_argument("--resamples", type=int, default=10_000)
    arguments = parser.parse_args()
    payload = json.loads(arguments.input.read_text(encoding="utf-8"))
    records = payload["records"] if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise AnalysisError("input must be a list or an object containing records")
    analysis = analyze_records(
        records,
        bootstrap_seed=arguments.bootstrap_seed,
        resamples=arguments.resamples,
    )
    write_figure_data(
        records,
        analysis,
        arguments.output,
        data_status=arguments.data_status,
        source_revision=arguments.source_revision,
    )
    print(json.dumps({key: value for key, value in analysis.items() if key != "estimates"}))


if __name__ == "__main__":
    main()
