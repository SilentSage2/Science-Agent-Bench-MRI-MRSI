# Architecture

The A1 core is deliberately small and provider-neutral.

```text
versioned TaskSpec                  model/mock Policy
        |                                  |
        v                                  v
   Evaluator <--- artifacts --- Executor <--- Action
        |                         |   |
        v                         |   +--- Tool registry (planned)
 deterministic grades            |
                                  +--- AgentStateMachine
                                  +--- BudgetLedger
                                  +--- TrajectoryWriter
```

The single-agent runner is the only component allowed to invoke tools. It intersects the task allowlist with an immutable registry, reserves budget before every model or tool call, owns state transitions, and records every action and observation before exposing the next state to the policy. Evaluators consume declared artifacts and runner events; policies never receive hidden reference values.

The current repository implements the contracts, state machine, budget ledger, trajectory writer, four generated task families, their deterministic graders, a scripted smoke policy, a provider-neutral model protocol, an offline-tested OpenAI Responses adapter, all three controller conditions, and an explicit tool registry. Production task-tool bindings, the remaining three task families, and container isolation remain planned.
