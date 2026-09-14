from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

from science_agent.agent import (
    AgentRunConfig,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetSpec, BudgetUsage
from science_agent.container_executor import (
    ContainerLimits,
    ContainerRequest,
    ContainerResult,
    DockerContainerExecutor,
)
from science_agent.contracts import Action, ActionKind
from science_agent.model import ModelRequest, ModelResult, ModelUsage
from science_agent.research.mri_multicoil import (
    create_multicoil_reconstruction_instance,
    run_multicoil_reconstruction,
)
from science_agent.research_task_tools import bind_multicoil_reconstruction
from science_agent.silent_invalidity import derive_silent_invalidity
from science_agent.trajectory import sha256_file


class HostFixtureExecutor:
    """Trusted test double; production bindings receive DockerContainerExecutor."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ContainerRequest) -> ContainerResult:
        self.calls += 1
        argv = request.argv
        method = argv[argv.index("--method") + 1]
        regularization = (
            float(argv[argv.index("--regularization") + 1]) if "--regularization" in argv else None
        )
        iterations = int(argv[argv.index("--iterations") + 1]) if "--iterations" in argv else None
        run_multicoil_reconstruction(
            request.input_directory,
            request.output_directory,
            method=method,
            regularization=regularization,
            iterations=iterations,
        )
        artifacts = {
            path.name: sha256_file(path)
            for path in sorted(request.output_directory.iterdir())
            if path.is_file()
        }
        artifact_bytes = sum(path.stat().st_size for path in request.output_directory.iterdir())
        return ContainerResult(0, "", "", 1, False, artifacts, artifact_bytes)


class ScriptedResearchModel:
    def __init__(self, actions: list[Action]) -> None:
        self._actions = iter(actions)

    @property
    def provider(self) -> str:
        return "scripted"

    @property
    def model(self) -> str:
        return "scripted-invalidity-test"

    def complete(self, request: ModelRequest) -> ModelResult:
        del request
        return ModelResult(
            provider=self.provider,
            model=self.model,
            response_id="scripted-response",
            action=next(self._actions),
            usage=ModelUsage(input_tokens=20, output_tokens=10),
        )


class ResearchTaskToolTests(unittest.TestCase):
    def _binding(self, root: Path, executor: HostFixtureExecutor) -> Any:
        create_multicoil_reconstruction_instance(
            root / "inputs",
            root / "evaluator",
            seed=1301,
            matrix_size=32,
            coils=4,
            acceleration=6.0,
            relative_noise=0.02,
        )
        return bind_multicoil_reconstruction(
            root / "inputs",
            root / "evaluator",
            root / "outputs",
            root / "work",
            executor,
        )

    def test_scientific_choices_are_allowed_but_paths_are_not(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = HostFixtureExecutor()
            binding = self._binding(root, executor)

            result = binding.tools.resolve("reconstruct_multicoil_mri").handler(
                {"method": "sense_cg", "regularization": 0.003, "iterations": 40}
            )

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)
            self.assertEqual(executor.calls, 1)

    def test_path_override_is_retryable_rejection_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = HostFixtureExecutor()
            binding = self._binding(root, executor)

            result = binding.tools.resolve("reconstruct_multicoil_mri").handler(
                {"method": "zero_filled", "output_directory": "/tmp/escape"}
            )

            self.assertFalse(result.observation.ok)
            self.assertTrue(result.observation.retryable)
            self.assertEqual(executor.calls, 0)

    def test_successful_tool_can_still_be_silently_scientifically_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = HostFixtureExecutor()
            binding = self._binding(root, executor)
            model = ScriptedResearchModel(
                [
                    Action(ActionKind.TOOL, "reconstruct_multicoil_mri", {"method": "zero_filled"}),
                    Action(
                        ActionKind.FINAL,
                        "submit",
                        {"validity_assessment": "uncertain"},
                    ),
                ]
            )
            config = AgentRunConfig(
                run_id="silent-invalidity-test",
                condition=ControllerCondition.REACTIVE,
                budget=BudgetSpec(
                    input_tokens=200,
                    output_tokens=100,
                    cost_microusd=1_000,
                    tool_calls=1,
                    wall_time_ms=120_000,
                    artifact_bytes=4_194_304,
                ),
                model_call_reservation=BudgetUsage(
                    input_tokens=100,
                    output_tokens=50,
                    cost_microusd=500,
                    wall_time_ms=10_000,
                ),
                max_model_calls=2,
                max_output_tokens=50,
                action_schema={"type": "object"},
                instructions="Choose one reconstruction and assess its scientific validity.",
                pricing=FixedTokenPricing(1_000, 1_000, "2026-09-14"),
            )
            run_directory = root / "run"

            result = MRIScienceAgent(model, binding.tools).run(
                binding.task, config, run_directory, binding.evaluator
            )
            self.assertIsNotNone(result.grade)
            assert result.grade is not None
            outcome = derive_silent_invalidity(run_directory / "trajectory.jsonl", result.grade)

            self.assertTrue(outcome.technically_completed)
            self.assertTrue(outcome.silent_invalidity)
            self.assertTrue(outcome.invalidity_detected)

    def test_result_metadata_contains_no_hidden_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executor = HostFixtureExecutor()
            binding = self._binding(root, executor)

            serialized = json.dumps(dict(binding.task.metadata)).lower()

            self.assertNotIn("seed", serialized)
            self.assertNotIn("reference", serialized)


@unittest.skipUnless(
    os.environ.get("SAB_RUN_DOCKER_TESTS") == "1" and os.environ.get("SAB_RESEARCH_IMAGE"),
    "set SAB_RUN_DOCKER_TESTS=1 and SAB_RESEARCH_IMAGE to test the research image",
)
class ResearchTaskDockerIntegrationTests(unittest.TestCase):
    def test_sense_candidate_runs_through_real_container_and_hidden_grader(self) -> None:
        image = os.environ["SAB_RESEARCH_IMAGE"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_multicoil_reconstruction_instance(
                root / "inputs",
                root / "evaluator",
                seed=1401,
                matrix_size=64,
                coils=8,
                acceleration=6.0,
                relative_noise=0.02,
            )
            executor = DockerContainerExecutor(
                limits=ContainerLimits(
                    image=image,
                    artifact_bytes=4_194_304,
                    file_size_bytes=4_194_304,
                )
            )
            binding = bind_multicoil_reconstruction(
                root / "inputs",
                root / "evaluator",
                root / "outputs",
                root / "work",
                executor,
            )

            result = binding.tools.resolve("reconstruct_multicoil_mri").handler(
                {"method": "sense_cg", "regularization": 0.003, "iterations": 40}
            )

            self.assertTrue(result.observation.ok, result.observation.payload)
            self.assertTrue(binding.evaluator().success)


if __name__ == "__main__":
    unittest.main()
