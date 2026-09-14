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
            |                                        (PLANNED)
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

The current repository implements the contracts, state machine, budget ledger, trajectory writer, four generated task families, their deterministic graders, a scripted smoke policy, a provider-neutral model protocol, an offline-tested OpenAI Responses adapter, all three controller conditions, an immutable tool registry, fixed-path trusted reference bindings, and a digest-pinned Docker execution boundary. Research-grade task bindings through that container boundary and the remaining three task families remain planned. Architecture figures must preserve this distinction and may not depict the trusted reference bindings as containerized research tools.
