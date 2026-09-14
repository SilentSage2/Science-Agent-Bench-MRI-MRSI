# Threat model

Model-authored code and tool arguments are untrusted. They may attempt path traversal, command injection, process spawning, resource exhaustion, environment inspection, network access, oversized output, or modification of inputs and graders.

The implemented execution boundary is a disposable, digest-pinned Docker container with no network, read-only task inputs and root filesystem, a fresh run-scoped output mount, host-mapped non-root execution, dropped capabilities, `no-new-privileges`, no host socket, an allowlisted executable, and CPU, memory, process, wall-time, per-file, captured-stream, and aggregate-artifact limits. The host executor rejects input links, bounds captured output, terminates noisy or timed-out containers, rejects unsafe artifact types and links, and records artifact hashes. It injects no credentials.

A subprocess wrapper alone is not a secure sandbox. The host subprocess in this implementation only invokes Docker with a constructed argument vector and no shell. CI checks command construction without requiring a privileged Docker daemon; the opt-in local integration suite (`SAB_RUN_DOCKER_TESTS=1 pytest tests/test_container_executor.py`) verifies that network, root-filesystem writes, and input writes are denied and that execution is non-root. Model-authored code must not be executed when this container boundary is unavailable.

Non-goals include resistance to kernel or container-runtime escape, side channels, malicious dependency supply chains, and denial of service beyond configured resource ceilings.

The public benchmark contains no private clinical data. Optional gated-data adapters must keep source scans and all restricted derivatives outside Git, strip credentials and local paths from trajectories, and follow the source agreement. Benchmark outputs are research artifacts and must not be used for diagnosis or patient care.
