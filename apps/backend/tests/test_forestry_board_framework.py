"""Unit tests for Forestry Board approval workflows and access control."""

import pytest

from forestry_board.roles import BoardMemberRole
from forestry_board.states import ApprovalStatus, WorkflowTransition
from forestry_board.signature import validate_signature, ElectronicSignature
from datetime import datetime


class TestBoardMemberRole:
    def test_has_county_access_same_county(self) -> None:
        assert BoardMemberRole.has_county_access(
            BoardMemberRole.FORESTRY_BOARD_MEMBER,
            "Baltimore",
            "Baltimore",
        ) is True

    def test_has_county_access_different_county(self) -> None:
        assert BoardMemberRole.has_county_access(
            BoardMemberRole.FORESTRY_BOARD_MEMBER,
            "Baltimore",
            "Montgomery",
        ) is False

    def test_has_county_access_case_insensitive(self) -> None:
        assert BoardMemberRole.has_county_access(
            BoardMemberRole.FORESTRY_BOARD_MEMBER,
            "baltimore",
            "Baltimore",
        ) is True

    def test_has_county_access_missing_county(self) -> None:
        assert BoardMemberRole.has_county_access(
            BoardMemberRole.FORESTRY_BOARD_MEMBER,
            None,
            "Baltimore",
        ) is False
        assert BoardMemberRole.has_county_access(
            BoardMemberRole.FORESTRY_BOARD_MEMBER,
            "Baltimore",
            None,
        ) is False


class TestWorkflowTransitions:
    def test_pending_to_approved(self) -> None:
        assert WorkflowTransition.can_transition(ApprovalStatus.PENDING, ApprovalStatus.APPROVED) is True

    def test_pending_to_revision_requested(self) -> None:
        assert WorkflowTransition.can_transition(
            ApprovalStatus.PENDING,
            ApprovalStatus.REVISION_REQUESTED,
        ) is True

    def test_approved_immutable(self) -> None:
        assert WorkflowTransition.can_transition(ApprovalStatus.APPROVED, ApprovalStatus.PENDING) is False
        assert WorkflowTransition.can_transition(ApprovalStatus.APPROVED, ApprovalStatus.REVISION_REQUESTED) is False


class TestElectronicSignature:
    def test_validate_signature_valid(self) -> None:
        ok, err = validate_signature("John Smith")
        assert ok is True
        assert err is None

    def test_validate_signature_too_short(self) -> None:
        ok, err = validate_signature("J")
        assert ok is False
        assert "at least" in (err or "")

    def test_validate_signature_required(self) -> None:
        ok, err = validate_signature("")
        assert ok is False
        assert "required" in (err or "")

    def test_validate_signature_matches_expected(self) -> None:
        ok, err = validate_signature("John Smith", expected_name="John Smith")
        assert ok is True

    def test_validate_signature_mismatch_expected(self) -> None:
        ok, err = validate_signature("John Doe", expected_name="John Smith")
        assert ok is False
        assert "match" in (err or "").lower()
