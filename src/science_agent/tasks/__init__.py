"""Generated scientific task fixtures and deterministic graders."""

from science_agent.tasks.mri_leakage_audit import (
    create_mri_leakage_fixture,
    grade_mri_leakage,
    solve_mri_leakage_reference,
)
from science_agent.tasks.mri_reconstruction import (
    create_mri_reconstruction_fixture,
    grade_mri_reconstruction,
    solve_mri_reconstruction_reference,
)
from science_agent.tasks.mrs_spectral_fit import (
    create_mrs_fit_fixture,
    grade_mrs_fit,
    solve_mrs_fit_reference,
)
from science_agent.tasks.mrsi_nuisance_removal import (
    create_mrsi_nuisance_fixture,
    grade_mrsi_nuisance,
    solve_mrsi_nuisance_reference,
)

__all__ = [
    "create_mri_leakage_fixture",
    "create_mri_reconstruction_fixture",
    "create_mrs_fit_fixture",
    "create_mrsi_nuisance_fixture",
    "grade_mri_leakage",
    "grade_mri_reconstruction",
    "grade_mrs_fit",
    "grade_mrsi_nuisance",
    "solve_mri_leakage_reference",
    "solve_mri_reconstruction_reference",
    "solve_mrs_fit_reference",
    "solve_mrsi_nuisance_reference",
]
