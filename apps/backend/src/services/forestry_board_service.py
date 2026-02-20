"""Forestry Board approval service: county-based access, electronic signature, revision tracking."""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from database.models import (
    Application,
    ContactInformation,
    ForestryBoard,
    ForestryBoardApproval,
    ProjectInformation,
    FinancialInformation,
    RevisionRequest,
)
from forestry_board.county_filter import get_application_county
from forestry_board.email_templates import (
    BOARD_REVIEW_REQUEST_SUBJECT,
    BOARD_REVIEW_REQUEST_BODY,
    BOARD_APPROVAL_CONFIRMATION_SUBJECT,
    BOARD_APPROVAL_CONFIRMATION_BODY,
    REVISION_REQUEST_NOTIFICATION_SUBJECT,
    REVISION_REQUEST_NOTIFICATION_BODY,
)
from forestry_board.signature import validate_signature
from forestry_board.states import ApprovalStatus
from utils.responses import error_response, success_response


def _get_email_service():
    try:
        from core.container import get_email_service
        return get_email_service()
    except Exception:
        return None


def _get_application_county_safe(app: Application) -> str | None:
    try:
        return get_application_county(app)
    except Exception:
        return None


class ForestryBoardService:
    """County-based application filtering, approval, and revision requests."""

    def mark_ready_for_board_review(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Mark application ready for board review; send notification to board."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        if app.status != "draft":
            return error_response("Only draft applications can be marked for board review", data={"code": "not_draft"})
        county = _get_application_county_safe(app)
        if not county:
            return error_response("County is required in contact information", data={"code": "county_required"})
        # Ensure contact info exists and is complete enough
        try:
            contact = ContactInformation.get(ContactInformation.application == app)
        except ContactInformation.DoesNotExist:
            return error_response("Contact information is required", data={"code": "contact_required"})
        app.ready_for_board_review_at = datetime.now(timezone.utc)
        app.save()
        try:
            approval = ForestryBoardApproval.get(ForestryBoardApproval.application == app)
            if approval.status == "revision_requested":
                approval.status = "pending"
                approval.save()
        except ForestryBoardApproval.DoesNotExist:
            pass
        board_emails = [b.email for b in ForestryBoard.select().where(ForestryBoard.county == county)]
        board_contact_email = board_emails[0] if board_emails else None
        if board_emails:
            subject = BOARD_REVIEW_REQUEST_SUBJECT
            body = BOARD_REVIEW_REQUEST_BODY.format(
                applicant_name=contact.primary_contact_name or "Applicant",
                organization_name=contact.organization_name or "",
                project_name=_get_project_name(app),
                county=county or "",
                review_link="{base_url}/board/review",
            )
            svc = _get_email_service()
            if svc:
                for email in board_emails:
                    svc.send(to=email, subject=subject, body_text=body)
        return success_response(
            data={"boardContactEmail": board_contact_email},
            message="Application marked ready for board review",
        )

    def list_applications_for_board_member(self, board_member_id: str) -> dict[str, Any]:
        """List applications from board member's county in review queue."""
        try:
            bmid = UUID(board_member_id)
        except (ValueError, TypeError):
            return error_response("Invalid board member id", data={"code": "invalid_id"})
        try:
            board = ForestryBoard.get(ForestryBoard.id == bmid)
        except ForestryBoard.DoesNotExist:
            return error_response("Board member not found", data={"code": "not_found"})
        county = board.county
        apps = (
            Application.select()
            .where(Application.ready_for_board_review_at.is_null(False))
            .order_by(Application.ready_for_board_review_at.desc())
        )
        out = []
        for app in apps:
            app_county = _get_application_county_safe(app)
            if app_county and app_county.strip().lower() == county.strip().lower():
                contact = _get_contact_or_none(app)
                proj = _get_project_or_none(app)
                out.append({
                    "applicationId": str(app.id),
                    "applicantName": contact.primary_contact_name if contact else "",
                    "organizationName": contact.organization_name if contact else "",
                    "projectName": proj.project_name if proj else "",
                    "county": app_county,
                    "status": _derive_approval_status(app),
                    "submittedForReviewDate": _format_datetime(app.ready_for_board_review_at),
                })
        return success_response(data={"applications": out})

    def get_application_for_board_member(self, board_member_id: str, application_id: str) -> dict[str, Any]:
        """Get full application details for board review with county access check."""
        try:
            bmid = UUID(board_member_id)
            aid = UUID(application_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            board = ForestryBoard.get(ForestryBoard.id == bmid)
        except ForestryBoard.DoesNotExist:
            return error_response("Board member not found", data={"code": "not_found"})
        try:
            app = Application.get(Application.id == aid)
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        app_county = _get_application_county_safe(app)
        if not app_county or app_county.strip().lower() != board.county.strip().lower():
            return error_response("Access denied: application not in your county", data={"code": "access_denied"})
        if not app.ready_for_board_review_at:
            return error_response("Application not submitted for board review", data={"code": "not_ready"})
        contact = _get_contact_or_none(app)
        proj = _get_project_or_none(app)
        fin = _get_financial_or_none(app)
        revision_history = [
            {
                "requestDate": r.created_at.isoformat().replace("+00:00", "Z") if r.created_at else None,
                "comments": r.comments,
            }
            for r in RevisionRequest.select().where(RevisionRequest.application == app).order_by(RevisionRequest.created_at)
        ]
        sections = {}
        if contact:
            sections["contactInformation"] = {
                "organization_name": contact.organization_name,
                "address_line1": contact.address_line1,
                "address_line2": contact.address_line2,
                "city": contact.city,
                "state_code": contact.state_code,
                "zip_code": contact.zip_code,
                "county": contact.county,
                "primary_contact_name": contact.primary_contact_name,
                "primary_contact_title": contact.primary_contact_title,
                "primary_contact_email": contact.primary_contact_email,
                "primary_contact_phone": contact.primary_contact_phone,
                "alternate_contact_name": contact.alternate_contact_name,
                "alternate_contact_title": contact.alternate_contact_title,
                "alternate_contact_email": contact.alternate_contact_email,
                "alternate_contact_phone": contact.alternate_contact_phone,
            }
        if proj:
            sections["projectInformation"] = {
                "project_name": proj.project_name,
                "site_address_line1": proj.site_address_line1,
                "site_address_line2": proj.site_address_line2,
                "site_city": proj.site_city,
                "site_state_code": proj.site_state_code,
                "site_zip_code": proj.site_zip_code,
                "site_ownership": proj.site_ownership,
                "project_type": proj.project_type,
                "acreage": proj.acreage,
                "tree_count": proj.tree_count,
                "start_date": proj.start_date.isoformat() if proj.start_date else None,
                "completion_date": proj.completion_date.isoformat() if proj.completion_date else None,
                "description": proj.description,
            }
        if fin:
            import json
            mf = json.loads(fin.matching_funds) if fin.matching_funds else None
            lib = json.loads(fin.line_item_budget) if fin.line_item_budget else None
            sections["financialInformation"] = {
                "total_project_cost": float(fin.total_project_cost) if fin.total_project_cost is not None else None,
                "grant_amount_requested": float(fin.grant_amount_requested) if fin.grant_amount_requested is not None else None,
                "matching_funds": mf,
                "line_item_budget": lib,
            }
        return success_response(data={
            "applicationId": str(app.id),
            "applicantName": contact.primary_contact_name if contact else "",
            "organizationName": contact.organization_name if contact else "",
            "projectName": proj.project_name if proj else "",
            "projectDescription": proj.description if proj else "",
            "county": app_county,
            "status": _derive_approval_status(app),
            "sections": sections,
            "revisionHistory": revision_history,
        })

    def approve(
        self,
        board_member_id: str,
        application_id: str,
        board_member_name: str,
        board_member_title: str | None,
        approval_date: datetime,
    ) -> dict[str, Any]:
        """Record approval with electronic signature. Enforces approval immutability."""
        try:
            bmid = UUID(board_member_id)
            aid = UUID(application_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            board = ForestryBoard.get(ForestryBoard.id == bmid)
        except ForestryBoard.DoesNotExist:
            return error_response("Board member not found", data={"code": "not_found"})
        try:
            app = Application.get(Application.id == aid)
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        app_county = _get_application_county_safe(app)
        if not app_county or app_county.strip().lower() != board.county.strip().lower():
            return error_response("Access denied: application not in your county", data={"code": "access_denied"})
        approval, created = ForestryBoardApproval.get_or_create(
            application=app,
            defaults={"board_member": board, "status": "pending"},
        )
        if approval.status == "approved":
            return error_response("Application already approved; approval cannot be revoked", data={"code": "already_approved"})
        if approval.status == "revision_requested":
            return error_response("Applicant must resubmit for review before approval", data={"code": "revision_pending"})
        ok, err = validate_signature(board_member_name, expected_name=board.board_member_name)
        if not ok:
            return error_response(err or "Invalid signature", data={"code": "invalid_signature"})
        approval.electronic_signature = board_member_name.strip()
        approval.approval_date = approval_date
        approval.status = "approved"
        approval.save()
        contact = _get_contact_or_none(app)
        applicant_email = contact.primary_contact_email if contact else None
        if applicant_email:
            svc = _get_email_service()
            if svc:
                svc.send(
                    to=applicant_email,
                    subject=BOARD_APPROVAL_CONFIRMATION_SUBJECT,
                    body_text=BOARD_APPROVAL_CONFIRMATION_BODY.format(
                        project_name=_get_project_name(app),
                        board_member_name=board.board_member_name,
                        approval_date=approval_date.strftime("%Y-%m-%d"),
                    ),
                )
        return success_response(
            data={"approvalTimestamp": approval.approval_date.isoformat().replace("+00:00", "Z") if approval.approval_date else None},
            message="Application approved",
        )

    def request_revision(
        self,
        board_member_id: str,
        application_id: str,
        comments: str,
    ) -> dict[str, Any]:
        """Request revisions with comments; creates revision history record."""
        try:
            bmid = UUID(board_member_id)
            aid = UUID(application_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            board = ForestryBoard.get(ForestryBoard.id == bmid)
        except ForestryBoard.DoesNotExist:
            return error_response("Board member not found", data={"code": "not_found"})
        try:
            app = Application.get(Application.id == aid)
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        app_county = _get_application_county_safe(app)
        if not app_county or app_county.strip().lower() != board.county.strip().lower():
            return error_response("Access denied: application not in your county", data={"code": "access_denied"})
        approval, _ = ForestryBoardApproval.get_or_create(
            application=app,
            defaults={"board_member": board, "status": "revision_requested"},
        )
        if approval.status == "approved":
            return error_response("Application already approved; cannot request revisions", data={"code": "already_approved"})
        comments_clean = (comments or "").strip()
        if not comments_clean:
            return error_response("Comments are required for revision request", data={"code": "comments_required"})
        rev_num = RevisionRequest.select().where(RevisionRequest.application == app).count() + 1
        RevisionRequest.create(application=app, board_member=board, comments=comments_clean, revision_number=rev_num)
        approval.status = "revision_requested"
        approval.save()
        contact = _get_contact_or_none(app)
        applicant_email = contact.primary_contact_email if contact else None
        if applicant_email:
            svc = _get_email_service()
            if svc:
                svc.send(
                    to=applicant_email,
                    subject=REVISION_REQUEST_NOTIFICATION_SUBJECT,
                    body_text=REVISION_REQUEST_NOTIFICATION_BODY.format(
                        project_name=_get_project_name(app),
                        comments=comments_clean,
                    ),
                )
        return success_response(message="Revision requested; applicant notified")

    def get_approval_status(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Get forestry board approval status for applicant."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        status = _derive_approval_status(app)
        result = {"status": status, "boardMemberName": None, "boardMemberTitle": None, "approvalDate": None, "revisionRequested": False, "revisionComments": None}
        try:
            approval = ForestryBoardApproval.get(ForestryBoardApproval.application == app)
            result["boardMemberName"] = approval.board_member.board_member_name
            result["boardMemberTitle"] = approval.board_member.title
            result["approvalDate"] = approval.approval_date.isoformat().replace("+00:00", "Z") if approval.approval_date else None
            result["revisionRequested"] = approval.status == "revision_requested"
            if approval.status == "revision_requested":
                latest = RevisionRequest.select().where(RevisionRequest.application == app).order_by(RevisionRequest.created_at.desc()).first()
                result["revisionComments"] = latest.comments if latest else None
        except ForestryBoardApproval.DoesNotExist:
            pass
        return success_response(data=result)


def _format_datetime(dt) -> str | None:
    """Format datetime for ISO 8601 API response."""
    if dt is None:
        return None
    if hasattr(dt, "isoformat"):
        return dt.isoformat().replace("+00:00", "Z")
    return str(dt)


def _get_contact_or_none(app: Application) -> ContactInformation | None:
    try:
        return ContactInformation.get(ContactInformation.application == app)
    except ContactInformation.DoesNotExist:
        return None


def _get_project_or_none(app: Application) -> ProjectInformation | None:
    try:
        return ProjectInformation.get(ProjectInformation.application == app)
    except ProjectInformation.DoesNotExist:
        return None


def _get_financial_or_none(app: Application) -> FinancialInformation | None:
    try:
        return FinancialInformation.get(FinancialInformation.application == app)
    except FinancialInformation.DoesNotExist:
        return None


def _get_project_name(app: Application) -> str:
    proj = _get_project_or_none(app)
    return proj.project_name or "Application" if proj else "Application"


def _derive_approval_status(app: Application) -> str:
    try:
        approval = ForestryBoardApproval.get(ForestryBoardApproval.application == app)
        return approval.status
    except ForestryBoardApproval.DoesNotExist:
        return "pending" if app.ready_for_board_review_at else "not_submitted"
