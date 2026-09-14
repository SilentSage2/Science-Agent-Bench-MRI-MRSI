from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from science_agent.container_executor import (
    ContainerLimits,
    ContainerRequest,
    ContainerResult,
    DockerContainerExecutor,
)
from science_agent.research.mrsi_nuisance import (
    create_complex_mrsi_instance,
    run_complex_mrsi_nuisance_removal,
)
from science_agent.research_task_tools import bind_complex_mrsi_nuisance
from science_agent.trajectory import sha256_file


class HostMRSIFixtureExecutor:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ContainerRequest) -> ContainerResult:
        self.calls += 1
        argv = request.argv
        method = argv[argv.index("--method") + 1]
        shift_steps = (
            int(argv[argv.index("--shift-steps") + 1]) if "--shift-steps" in argv else None
        )
        run_complex_mrsi_nuisance_removal(
            request.input_directory,
            request.output_directory,
            method=method,
            shift_steps=shift_steps,
        )
        hashes = {
            path.name: sha256_file(path)
            for path in sorted(request.output_directory.iterdir())
            if path.is_file()
        }
        artifact_bytes = sum(path.stat().st_size for path in request.output_directory.iterdir())
        return ContainerResult(0, "", "", 1, False, hashes, artifact_bytes)


class ComplexMRSIResearchToolTests(unittest.TestCase):
    def test_adaptive_choice_runs_and_passes_hidden_grader(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(
                root / "inputs",
                root / "evaluator",
                seed=301,
                grid_size=3,
                difficulty="hard",
            )
            executor = HostMRSIFixtureExecutor()
            binding = bind_complex_mrsi_nuisance(
                root / "inputs", root / "evaluator", root / "outputs", root / "work", executor
            )

            result = binding.tools.resolve("remove_complex_mrsi_nuisance").handler(
                {"method": "adaptive_projection", "shift_steps": 21}
            )

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)
            self.assertEqual(executor.calls, 1)

    def test_paths_and_hidden_references_are_not_policy_controlled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(root / "inputs", root / "evaluator", seed=302, grid_size=3)
            executor = HostMRSIFixtureExecutor()
            binding = bind_complex_mrsi_nuisance(
                root / "inputs", root / "evaluator", root / "outputs", root / "work", executor
            )

            result = binding.tools.resolve("remove_complex_mrsi_nuisance").handler(
                {
                    "method": "adaptive_projection",
                    "shift_steps": 21,
                    "evaluator_directory": "/tmp/escape",
                }
            )

            self.assertFalse(result.observation.ok)
            self.assertTrue(result.observation.retryable)
            self.assertEqual(executor.calls, 0)
            serialized = json.dumps(dict(binding.task.metadata)).lower()
            self.assertNotIn("seed", serialized)
            self.assertNotIn("reference", serialized)


@unittest.skipUnless(
    os.environ.get("SAB_RUN_DOCKER_TESTS") == "1" and os.environ.get("SAB_RESEARCH_IMAGE"),
    "set SAB_RUN_DOCKER_TESTS=1 and SAB_RESEARCH_IMAGE to test the research image",
)
class ComplexMRSIDockerIntegrationTests(unittest.TestCase):
    def test_adaptive_candidate_runs_in_real_container(self) -> None:
        image = os.environ["SAB_RESEARCH_IMAGE"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(
                root / "inputs", root / "evaluator", seed=303, grid_size=3, difficulty="hard"
            )
            executor = DockerContainerExecutor(
                limits=ContainerLimits(
                    image=image,
                    artifact_bytes=4_194_304,
                    file_size_bytes=4_194_304,
                )
            )
            binding = bind_complex_mrsi_nuisance(
                root / "inputs", root / "evaluator", root / "outputs", root / "work", executor
            )

            result = binding.tools.resolve("remove_complex_mrsi_nuisance").handler(
                {"method": "adaptive_projection", "shift_steps": 21}
            )

            self.assertTrue(result.observation.ok, result.observation.payload)
            self.assertTrue(binding.evaluator().success)


if __name__ == "__main__":
    unittest.main()
