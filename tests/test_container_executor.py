from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from science_agent.container_executor import (
    PINNED_PYTHON_IMAGE,
    ContainerExecutionError,
    ContainerLimits,
    ContainerRequest,
    DockerContainerExecutor,
)


class ContainerCommandTests(unittest.TestCase):
    def test_command_contains_security_boundary_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            request = ContainerRequest(inputs, root / "outputs", ("python", "-c", "pass"))

            command = DockerContainerExecutor().build_command(request, "sab-" + "a" * 32)

        rendered = " ".join(command)
        self.assertIn("--network none", rendered)
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop ALL", rendered)
        self.assertIn("no-new-privileges=true", command)
        self.assertIn("readonly", rendered)
        self.assertIn(PINNED_PYTHON_IMAGE, command)

    def test_unpinned_image_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ContainerLimits(image="python:3.12-slim")

    def test_exact_local_image_id_is_accepted(self) -> None:
        image = "sha256:" + "a" * 64

        self.assertEqual(ContainerLimits(image=image).image, image)

    def test_non_allowlisted_executable_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            request = ContainerRequest(inputs, root / "outputs", ("sh", "-c", "id"))

            with self.assertRaises(ContainerExecutionError):
                DockerContainerExecutor().build_command(request, "sab-" + "a" * 32)

    def test_input_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            (inputs / "link").symlink_to(root)
            request = ContainerRequest(inputs, root / "outputs", ("python", "-c", "pass"))

            with self.assertRaises(ContainerExecutionError):
                DockerContainerExecutor().build_command(request, "sab-" + "a" * 32)


@unittest.skipUnless(
    os.environ.get("SAB_RUN_DOCKER_TESTS") == "1",
    "set SAB_RUN_DOCKER_TESTS=1 to exercise the local Docker boundary",
)
class DockerBoundaryIntegrationTests(unittest.TestCase):
    def test_container_is_non_root_offline_and_read_only(self) -> None:
        script = """
import json
import os
import socket
from pathlib import Path

checks = {"non_root": os.geteuid() != 0}
for name, action in {
    "network_denied": lambda: socket.create_connection(("1.1.1.1", 53), timeout=0.5),
    "root_read_only": lambda: Path("/blocked.txt").write_text("blocked"),
    "input_read_only": lambda: Path("/inputs/value.txt").write_text("blocked"),
}.items():
    try:
        action()
    except OSError:
        checks[name] = True
    else:
        checks[name] = False

value = Path("/inputs/value.txt").read_text(encoding="utf-8")
Path("/outputs/result.json").write_text(
    json.dumps({"checks": checks, "value": value}), encoding="utf-8"
)
print("boundary-check-complete")
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            (inputs / "value.txt").write_text("MRI-MRSI", encoding="utf-8")
            outputs = root / "outputs"

            result = DockerContainerExecutor().execute(
                ContainerRequest(inputs, outputs, ("python", "-c", script))
            )

            self.assertEqual(result.exit_code, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "boundary-check-complete")
            self.assertIn("result.json", result.artifact_hashes)
            payload = (outputs / "result.json").read_text(encoding="utf-8")
            self.assertIn('"non_root": true', payload)
            self.assertIn('"network_denied": true', payload)
            self.assertIn('"root_read_only": true', payload)
            self.assertIn('"input_read_only": true', payload)
            self.assertIn('"value": "MRI-MRSI"', payload)

    def test_stream_limit_terminates_noisy_container(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            inputs.mkdir()
            limits = ContainerLimits(stream_bytes=8_192, captured_stream_bytes=4_096)
            executor = DockerContainerExecutor(limits=limits)

            with self.assertRaisesRegex(ContainerExecutionError, "stdout/stderr"):
                executor.execute(
                    ContainerRequest(
                        inputs,
                        root / "outputs",
                        ("python", "-c", "while True: print('x' * 1024)"),
                    )
                )


if __name__ == "__main__":
    unittest.main()
