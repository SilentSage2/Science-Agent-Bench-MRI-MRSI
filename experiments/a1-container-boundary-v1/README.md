# A1 container boundary validation v1

## Purpose

Validate the security controls required before any model-authored MRI/MRSI workload can execute. This is an infrastructure result, not a model or scientific result.

## Frozen setup

- Date: 2026-09-14
- Runtime: Docker 29.7.2
- Image: `python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7`
- Network: none
- Root filesystem and input mount: read-only
- Identity: non-root host UID/GID mapping
- Capabilities: all dropped; `no-new-privileges` enabled
- Default ceilings: 1 CPU, 1 GiB memory, 64 processes, 60 seconds, 1 MiB per file, 1 MiB aggregate artifacts, and 1 MiB combined stdout/stderr

## Result

The real-container integration suite passed 2/2 tests. The first test verified successful input reading and artifact creation while confirming that network access, root-filesystem writes, and input writes were denied and execution was non-root. The second test verified forced termination when combined stdout/stderr exceeded its hard host-side limit.

Four additional offline tests passed for security-flag construction, digest pinning, executable allowlisting, and input-link rejection. The full repository suite passed 67 tests with the two Docker tests skipped by default; the explicit Docker run passed all six executor tests.

This result does not establish resistance to container-runtime or kernel escape, side channels, supply-chain attacks, or denial of service below configured ceilings. It also does not authorize model-authored execution until an allowlisted task binding uses this boundary.

## Reproduction

```bash
SAB_RUN_DOCKER_TESTS=1 PYTHONPATH=src pytest tests/test_container_executor.py
```
