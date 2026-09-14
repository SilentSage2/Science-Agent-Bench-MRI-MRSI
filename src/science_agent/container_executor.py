"""Docker execution boundary for untrusted benchmark tool workloads."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from selectors import EVENT_READ, DefaultSelector

PINNED_PYTHON_IMAGE = (
    "python:3.12.11-slim-bookworm@"
    "sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7"
)


class ContainerExecutionError(RuntimeError):
    """Raised when an execution request or produced artifact tree is unsafe."""


@dataclass(frozen=True, slots=True)
class ContainerLimits:
    """Resource ceilings applied independently to every container run."""

    image: str = PINNED_PYTHON_IMAGE
    cpus: str = "1.0"
    memory_bytes: int = 1_073_741_824
    pids: int = 64
    timeout_seconds: float = 60.0
    tmpfs_bytes: int = 67_108_864
    file_size_bytes: int = 1_048_576
    artifact_bytes: int = 1_048_576
    artifact_files: int = 128
    stream_bytes: int = 1_048_576
    captured_stream_bytes: int = 262_144

    def __post_init__(self) -> None:
        registry_digest = "@sha256:" in self.image
        local_image_id = re.fullmatch(r"sha256:[a-f0-9]{64}", self.image) is not None
        if not registry_digest and not local_image_id:
            raise ValueError("container image must be pinned by registry digest or local image ID")
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", self.cpus):
            raise ValueError("cpus must be a positive decimal string")
        if float(self.cpus) <= 0:
            raise ValueError("cpus must be positive")
        integer_limits = (
            self.memory_bytes,
            self.pids,
            self.tmpfs_bytes,
            self.file_size_bytes,
            self.artifact_bytes,
            self.artifact_files,
            self.stream_bytes,
            self.captured_stream_bytes,
        )
        if any(value <= 0 for value in integer_limits) or self.timeout_seconds <= 0:
            raise ValueError("container limits must be positive")
        if self.captured_stream_bytes > self.stream_bytes:
            raise ValueError("captured stream limit cannot exceed stream limit")


@dataclass(frozen=True, slots=True)
class ContainerRequest:
    input_directory: Path
    output_directory: Path
    argv: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ContainerResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    stream_truncated: bool
    artifact_hashes: dict[str, str]
    artifact_bytes: int


@dataclass(frozen=True, slots=True)
class _ProcessOutput:
    stdout: bytes
    stderr: bytes
    stream_truncated: bool
    limit_exceeded: bool
    timed_out: bool


class DockerContainerExecutor:
    """Run a fixed, allowlisted argv inside a constrained Docker container."""

    def __init__(
        self,
        *,
        docker_binary: str = "docker",
        allowed_executables: tuple[str, ...] = ("python", "python3"),
        limits: ContainerLimits | None = None,
    ) -> None:
        if not allowed_executables or any("/" in item or not item for item in allowed_executables):
            raise ValueError("allowed executables must be non-empty command names")
        self._docker_binary = docker_binary
        self._allowed_executables = frozenset(allowed_executables)
        self._limits = limits or ContainerLimits()

    def build_command(self, request: ContainerRequest, container_name: str) -> list[str]:
        """Validate a request and build argv without invoking a shell."""
        inputs = request.input_directory.resolve(strict=True)
        outputs = request.output_directory.resolve(strict=False)
        if not inputs.is_dir():
            raise ContainerExecutionError("input path must be a directory")
        if request.output_directory.exists():
            raise ContainerExecutionError("output directory must not already exist")
        if not request.argv or request.argv[0] not in self._allowed_executables:
            raise ContainerExecutionError("container executable is not allowlisted")
        if len(request.argv) > 128 or any(not arg or "\x00" in arg for arg in request.argv):
            raise ContainerExecutionError("container argv is invalid")
        if not re.fullmatch(r"sab-[a-f0-9]{32}", container_name):
            raise ContainerExecutionError("container name is invalid")
        self._reject_links(inputs)

        uid = os.getuid()
        gid = os.getgid()
        return [
            self._docker_binary,
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--user",
            f"{uid}:{gid}",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges=true",
            "--pids-limit",
            str(self._limits.pids),
            "--memory",
            str(self._limits.memory_bytes),
            "--cpus",
            self._limits.cpus,
            "--ulimit",
            f"fsize={self._limits.file_size_bytes}:{self._limits.file_size_bytes}",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,nodev,size={self._limits.tmpfs_bytes}",
            "--mount",
            f"type=bind,src={inputs},dst=/inputs,readonly",
            "--mount",
            f"type=bind,src={outputs},dst=/outputs",
            "--workdir",
            "/tmp",
            "--env",
            "HOME=/tmp",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            "PYTHONHASHSEED=0",
            self._limits.image,
            *request.argv,
        ]

    def execute(self, request: ContainerRequest) -> ContainerResult:
        """Execute a request and validate every returned artifact."""
        name = f"sab-{uuid.uuid4().hex}"
        command = self.build_command(request, name)
        request.output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
        started = time.monotonic()
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
            )
        except OSError as exc:
            raise ContainerExecutionError("Docker could not be started") from exc

        output = self._collect_output(process, name)
        exit_code = process.wait()
        duration_ms = max(0, int((time.monotonic() - started) * 1_000))
        if output.timed_out:
            raise ContainerExecutionError("container exceeded wall-time limit")
        if output.limit_exceeded:
            raise ContainerExecutionError("container exceeded stdout/stderr limit")

        hashes, artifact_bytes = self._validate_artifacts(request.output_directory)
        return ContainerResult(
            exit_code=exit_code,
            stdout=output.stdout.decode("utf-8", errors="replace"),
            stderr=output.stderr.decode("utf-8", errors="replace"),
            duration_ms=duration_ms,
            stream_truncated=output.stream_truncated,
            artifact_hashes=hashes,
            artifact_bytes=artifact_bytes,
        )

    def _collect_output(self, process: subprocess.Popen[bytes], name: str) -> _ProcessOutput:
        if process.stdout is None or process.stderr is None:
            raise ContainerExecutionError("Docker output pipes are unavailable")
        selector = DefaultSelector()
        selector.register(process.stdout, EVENT_READ, "stdout")
        selector.register(process.stderr, EVENT_READ, "stderr")
        captured = {"stdout": bytearray(), "stderr": bytearray()}
        observed = 0
        truncated = False
        deadline = time.monotonic() + self._limits.timeout_seconds
        timed_out = False
        limit_exceeded = False

        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            for key, _ in selector.select(timeout=min(0.1, remaining)):
                chunk = os.read(key.fd, 65_536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                observed += len(chunk)
                target = captured[str(key.data)]
                available = self._limits.captured_stream_bytes - sum(
                    len(value) for value in captured.values()
                )
                if available > 0:
                    target.extend(chunk[:available])
                if available < len(chunk):
                    truncated = True
                if observed > self._limits.stream_bytes:
                    limit_exceeded = True
                    break
            if limit_exceeded:
                break

        if timed_out or limit_exceeded:
            self._force_remove(name)
            process.kill()
            process.wait(timeout=5)
        selector.close()
        return _ProcessOutput(
            stdout=bytes(captured["stdout"]),
            stderr=bytes(captured["stderr"]),
            stream_truncated=truncated,
            limit_exceeded=limit_exceeded,
            timed_out=timed_out,
        )

    def _force_remove(self, name: str) -> None:
        try:
            subprocess.run(
                [self._docker_binary, "rm", "--force", name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    def _validate_artifacts(self, output_directory: Path) -> tuple[dict[str, str], int]:
        hashes: dict[str, str] = {}
        total_bytes = 0
        file_count = 0
        for path in sorted(output_directory.rglob("*")):
            relative = path.relative_to(output_directory).as_posix()
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise ContainerExecutionError("artifact links are forbidden")
            if path.is_dir():
                continue
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise ContainerExecutionError("artifact must be a regular, unlinked file")
            file_count += 1
            total_bytes += metadata.st_size
            if file_count > self._limits.artifact_files:
                raise ContainerExecutionError("container produced too many artifacts")
            if metadata.st_size > self._limits.file_size_bytes:
                raise ContainerExecutionError("artifact exceeded per-file size limit")
            if total_bytes > self._limits.artifact_bytes:
                raise ContainerExecutionError("artifacts exceeded total size limit")
            hashes[relative] = _sha256_file(path)
        return hashes, total_bytes

    @staticmethod
    def _reject_links(directory: Path) -> None:
        for path in directory.rglob("*"):
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise ContainerExecutionError("input links are forbidden")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()
