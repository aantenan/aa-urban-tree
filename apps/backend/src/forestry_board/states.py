"""Approval workflow state management patterns and transitions."""

from enum import Enum


class ApprovalStatus(str, Enum):
    """Forestry Board approval status for an application."""

    PENDING = "pending"
    APPROVED = "approved"
    REVISION_REQUESTED = "revision_requested"


class WorkflowTransition:
    """
    Valid workflow transitions for board approval.
    - PENDING: awaiting board review
    - APPROVED: board approved (immutable)
    - REVISION_REQUESTED: board requested changes; applicant can resubmit for review
    """

    ALLOWED: dict[ApprovalStatus, list[ApprovalStatus]] = {
        ApprovalStatus.PENDING: [ApprovalStatus.APPROVED, ApprovalStatus.REVISION_REQUESTED],
        ApprovalStatus.REVISION_REQUESTED: [ApprovalStatus.PENDING],  # after applicant resubmits
        ApprovalStatus.APPROVED: [],  # no transitions - immutable
    }

    @classmethod
    def can_transition(cls, from_status: ApprovalStatus, to_status: ApprovalStatus) -> bool:
        return to_status in cls.ALLOWED.get(from_status, [])
