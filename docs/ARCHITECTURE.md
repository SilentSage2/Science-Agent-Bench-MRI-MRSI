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

The executor will be the only component allowed to invoke tools. It owns state transitions and budget reservation, and records every action and observation before exposing the next state to the policy. Evaluators consume declared artifacts and executor events; policies never receive hidden reference values.

The current repository implements the contracts, state machine, budget ledger, and trajectory writer. Tool execution, task graders, policies, orchestration, and container isolation remain planned.

