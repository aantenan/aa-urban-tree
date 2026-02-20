"""Unit tests for Forestry Board approval service."""
from datetime import datetime, timezone

import pytest

from database.models import (
    Application,
    ContactInformation,
    ForestryBoard,
    ForestryBoardApproval,
    ProjectInformation,
    RevisionRequest,
    User,
)
from services.forestry_board_service import ForestryBoardService


@pytest.fixture
def user(memory_db):
    return User.create(email="applicant@test.com", password_hash="hash", account_status="active")


@pytest.fixture
def board_user(memory_db):
    return User.create(email="board@test.com", password_hash="hash", account_status="active")


@pytest.fixture
def board_member(board_user):
    return ForestryBoard.create(
        user=board_user,
        county="Baltimore",
        board_member_name="Jane Reviewer",
        title="Board Chair",
        email=board_user.email,
    )


@pytest.fixture
def application(user):
    return Application.create(user=user, status="draft")


@pytest.fixture
def application_with_contact(application, user):
    ContactInformation.create(
        application=application,
        organization_name="Test Org",
        address_line1="123 Main St",
        city="Baltimore",
        state_code="MD",
        zip_code="21201",
        county="Baltimore",
        primary_contact_name="John Applicant",
        primary_contact_email="applicant@test.com",
    )
    return application


@pytest.fixture
def service():
    return ForestryBoardService()


def test_mark_ready_for_board_review_success(service, application_with_contact, user):
    result = service.mark_ready_for_board_review(str(application_with_contact.id), str(user.id))
    assert result["success"] is True
    app = Application.get_by_id(application_with_contact.id)
    assert app.ready_for_board_review_at is not None


def test_mark_ready_for_board_review_no_county(service, application, user):
    ContactInformation.create(
        application=application,
        organization_name="Test",
        county=None,
        primary_contact_name="John",
        primary_contact_email="j@test.com",
    )
    result = service.mark_ready_for_board_review(str(application.id), str(user.id))
    assert result["success"] is False
    assert result["data"]["code"] == "county_required"


def test_list_applications_for_board_member_empty(service, board_member):
    result = service.list_applications_for_board_member(str(board_member.id))
    assert result["success"] is True
    assert result["data"]["applications"] == []


def test_list_applications_for_board_member_filtered(service, board_member, application_with_contact):
    application_with_contact.ready_for_board_review_at = datetime.now(timezone.utc)
    application_with_contact.save()
    result = service.list_applications_for_board_member(str(board_member.id))
    assert result["success"] is True
    assert len(result["data"]["applications"]) == 1
    assert result["data"]["applications"][0]["county"] == "Baltimore"
    assert result["data"]["applications"][0]["applicantName"] == "John Applicant"


def test_get_application_access_denied_wrong_county(service, board_member, application_with_contact):
    application_with_contact.ready_for_board_review_at = datetime.now(timezone.utc)
    application_with_contact.save()
    ContactInformation.update(county="Montgomery").where(
        ContactInformation.application == application_with_contact
    ).execute()
    result = service.get_application_for_board_member(str(board_member.id), str(application_with_contact.id))
    assert result["success"] is False
    assert result["data"]["code"] == "access_denied"


def test_approve_success(service, board_member, application_with_contact):
    application_with_contact.ready_for_board_review_at = datetime.now(timezone.utc)
    application_with_contact.save()
    result = service.approve(
        str(board_member.id),
        str(application_with_contact.id),
        board_member.board_member_name,
        board_member.title,
        datetime.now(timezone.utc),
    )
    assert result["success"] is True
    approval = ForestryBoardApproval.get(ForestryBoardApproval.application == application_with_contact)
    assert approval.status == "approved"
    assert approval.electronic_signature == "Jane Reviewer"


def test_approve_invalid_signature(service, board_member, application_with_contact):
    application_with_contact.ready_for_board_review_at = datetime.now(timezone.utc)
    application_with_contact.save()
    result = service.approve(
        str(board_member.id),
        str(application_with_contact.id),
        "Wrong Name",
        None,
        datetime.now(timezone.utc),
    )
    assert result["success"] is False
    assert result["data"]["code"] == "invalid_signature"


def test_request_revision_success(service, board_member, application_with_contact):
    application_with_contact.ready_for_board_review_at = datetime.now(timezone.utc)
    application_with_contact.save()
    result = service.request_revision(str(board_member.id), str(application_with_contact.id), "Please add more detail.")
    assert result["success"] is True
    rev = RevisionRequest.get(RevisionRequest.application == application_with_contact)
    assert rev.comments == "Please add more detail."
