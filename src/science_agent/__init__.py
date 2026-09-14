"""Provider-neutral core contracts for Science Agent Bench."""

from science_agent.agent import (
    AgentRunConfig,
    AgentRunResult,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetExceeded, BudgetLedger, BudgetSpec, BudgetUsage
from science_agent.contracts import Action, ActionKind, Observation, TaskSpec
from science_agent.model import ModelAdapter, ModelError, ModelRequest, ModelResult, ModelUsage
from science_agent.openai_responses import ModelAdapterError, OpenAIResponsesAdapter
from science_agent.state import AgentPhase, AgentStateMachine, InvalidTransition
from science_agent.task_tools import (
    ReferenceTaskBinding,
    TaskBindingError,
    bind_mri_leakage_reference,
    bind_mri_reconstruction_reference,
    bind_mrs_fit_reference,
    bind_mrsi_nuisance_reference,
)
from science_agent.tools import RegisteredTool, ToolRegistry, ToolResult
from science_agent.trajectory import TrajectoryEvent, TrajectoryWriter, sha256_file

__all__ = [
    "Action",
    "ActionKind",
    "AgentPhase",
    "AgentRunConfig",
    "AgentRunResult",
    "AgentStateMachine",
    "BudgetExceeded",
    "BudgetLedger",
    "BudgetSpec",
    "BudgetUsage",
    "ControllerCondition",
    "FixedTokenPricing",
    "InvalidTransition",
    "MRIScienceAgent",
    "ModelAdapter",
    "ModelAdapterError",
    "ModelError",
    "ModelRequest",
    "ModelResult",
    "ModelUsage",
    "Observation",
    "OpenAIResponsesAdapter",
    "ReferenceTaskBinding",
    "RegisteredTool",
    "TaskBindingError",
    "TaskSpec",
    "ToolRegistry",
    "ToolResult",
    "TrajectoryEvent",
    "TrajectoryWriter",
    "bind_mri_leakage_reference",
    "bind_mri_reconstruction_reference",
    "bind_mrs_fit_reference",
    "bind_mrsi_nuisance_reference",
    "sha256_file",
]
