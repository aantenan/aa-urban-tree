"""Email notification templates for board review requests and approval confirmations."""

BOARD_REVIEW_REQUEST_SUBJECT = "Forestry Board Review: New application ready for review"

BOARD_REVIEW_REQUEST_BODY = """
An application has been marked ready for Forestry Board review.

Applicant: {applicant_name}
Organization: {organization_name}
Project: {project_name}
County: {county}

Please log in to the application portal to review and approve or request revisions.

Review link: {review_link}
"""

BOARD_APPROVAL_CONFIRMATION_SUBJECT = "Forestry Board Approval: Your application has been approved"

BOARD_APPROVAL_CONFIRMATION_BODY = """
Your application has been approved by the Forestry Board.

Application: {project_name}
Approved by: {board_member_name}
Approval date: {approval_date}

You may now proceed with submission to MDOT.
"""

REVISION_REQUEST_NOTIFICATION_SUBJECT = "Forestry Board: Revision requested for your application"

REVISION_REQUEST_NOTIFICATION_BODY = """
The Forestry Board has requested revisions to your application.

Application: {project_name}
Comments: {comments}

Please log in to view the full feedback, make the requested changes, and resubmit for board review when ready.
"""
