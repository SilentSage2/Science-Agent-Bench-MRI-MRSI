# Threat model

Model-authored code and tool arguments are untrusted. They may attempt path traversal, command injection, process spawning, resource exhaustion, environment inspection, network access, oversized output, or modification of inputs and graders.

The intended execution boundary is a disposable, version-pinned container with no network, read-only task inputs and runtime, a fresh run-scoped output mount, non-root execution, dropped capabilities, no host socket, an allowlisted entry point, and hard CPU, memory, process, time, file-size, and output limits. The host executor must validate paths and artifact hashes after execution and must not inject credentials.

A subprocess wrapper is not a secure sandbox. Until the container boundary exists and its denial controls are tested, CI must use only scripted mock actions and must not execute model-authored code.

Non-goals include resistance to kernel or container-runtime escape, side channels, malicious dependency supply chains, and denial of service beyond configured resource ceilings.

The public benchmark contains no private clinical data. Optional gated-data adapters must keep source scans and all restricted derivatives outside Git, strip credentials and local paths from trajectories, and follow the source agreement. Benchmark outputs are research artifacts and must not be used for diagnosis or patient care.
