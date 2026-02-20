# Forestry Board Approval Workflow

## Overview

The Forestry Board Approval Workflow enables County Forestry Board members to review applications from their jurisdiction and provide mandatory endorsement before submission to MDOT.

## Flow

1. Applicant completes their application and marks it as "ready for board review."
2. The system identifies the applicant's county and sends an email notification to the corresponding Forestry Board.
3. Board members authenticate and view applications from their county in a review queue.
4. Board members can:
   - **Approve** applications with an electronic signature (typed name confirmation)
   - **Request revisions** with comments that the applicant can view and address
5. Applicants are notified of approval or revision requests.

## Electronic Signature

Electronic signatures are captured as typed name confirmations with timestamps:

- The board member types their full name to confirm their approval
- The system validates that the typed name matches the board member's registered name
- A timestamp is recorded with each approval
- Signatures are immutable once recorded

## Approval Immutability

Once a board member approves an application, the approval cannot be revoked. If changes are needed after approval, the applicant must withdraw and resubmit.

## County-Based Access

Board member access is restricted to applications from their assigned county, enforced at the API level. Board members cannot view or act on applications from other jurisdictions.

## Revision Requests

When a board member requests revisions:

- Comments are stored in the revision history
- The applicant receives an email notification
- The applicant can edit and resubmit for re-review
- Previous revision comments remain visible in the revision history
