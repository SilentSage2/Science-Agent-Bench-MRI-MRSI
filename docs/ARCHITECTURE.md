# Architecture

The A1 core is deliberately small and provider-neutral.

```text
public TaskSpec + inputs       model adapter + frozen controller
            |                              |
            v                              v
      MRIScienceAgent ---- typed Action --> immutable ToolRegistry
            |                              |
            |                       reserve hard budget
            |                              |
            |                 +------------+-------------+
            |                 |                          |
            |        trusted reference binding    Docker boundary
            |        (current smoke path)         (implemented/tested)
            |                                            |
            |                                  research task binding
            |                                  (MRI + MRSI implemented)
            |                 |                          |
            +<--- typed Observation + artifact hashes --+
            |
            +----> append-only trajectory + run manifest
            |
            +----> scientific artifacts ----> deterministic Evaluator
                                                   ^
                                                   |
                                         hidden references (isolated)
```

The single-agent runner is the only component allowed to invoke tools. It intersects the task allowlist with an immutable registry, reserves budget before every model or tool call, owns state transitions, and records every action and observation before exposing the next state to the policy. Evaluators consume declared artifacts and runner events; policies never receive hidden reference values.

The repository implements the contracts, state machine, budget ledger, trajectory writer, four development task families, a provider-neutral model protocol, all five controller paths, fixed-path trusted reference bindings, and a digest-pinned Docker boundary. Research-candidate multi-coil MRI and complex-MRSI bindings now traverse that boundary with evaluator-isolated references. A 10-cell real-model development checkout has run; the signed frozen primary study and public/challenge physics/domain validation remain planned. Secondary families do not become requirements merely to increase task count. Architecture figures must distinguish trusted dry-run bindings from containerized research tools.
