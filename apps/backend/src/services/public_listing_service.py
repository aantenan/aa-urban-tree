"""Public listing service: configuration management and caching for program information."""
from typing import Any

from services.program_config import get_cached_program_config
from models.program import ProgramConfig


class PublicListingService:
    """Manages program configuration and caching for public listing API."""

    def __init__(self) -> None:
        pass

    def get_program_config(self) -> tuple[ProgramConfig, str]:
        """
        Return cached program config and etag for conditional GET.
        No authentication required.
        """
        return get_cached_program_config()

    def get_program_config_api_response(self) -> dict[str, Any]:
        """
        Return program configuration in API shape for GET /api/config/program.
        Includes program, grant_cycle, eligibility, resources with SEO-friendly structure.
        """
        config, _ = self.get_program_config()

        # Build program section
        prog = config.program
        program = {
            "name": prog.name if prog else config.title,
            "purpose": prog.purpose if prog else config.description,
            "fundingAvailable": prog.funding_available if prog else None,
            "contactEmail": (prog.contact_email if prog else None) or config.contact_email,
            "contactPhone": (prog.contact_phone if prog else None) or config.contact_phone,
        }

        # Build grant cycle
        gc = config.grant_cycle
        grant_cycle = {}
        if gc:
            grant_cycle = {
                "year": gc.year,
                "applicationOpen": gc.application_open,
                "applicationDeadline": gc.application_deadline,
                "awardNotificationDate": gc.award_notification_date,
            }

        # Build eligibility
        ec = config.eligibility_config
        eligibility = {}
        if ec:
            fl = ec.funding_limits
            funding_limits = (
                {"minimum": fl.minimum, "maximum": fl.maximum} if fl else None
            )
            eligibility = {
                "applicantTypes": ec.applicant_types,
                "projectTypes": ec.project_types,
                "fundingLimits": funding_limits,
                "costMatchRequirement": ec.cost_match_requirement,
                "ineligibleActivities": ec.ineligible_activities,
                "summary": ec.summary,
            }

        # Build resources (camelCase for API)
        resources = []
        for r in config.resources:
            resources.append({
                "id": r.id,
                "title": r.title or r.label,
                "label": r.label,
                "description": r.description,
                "url": r.url,
                "storageKey": r.storage_key,
                "fileType": r.file_type,
            })

        return {
            "program": program,
            "grantCycle": grant_cycle,
            "eligibility": eligibility,
            "resources": resources,
            "title": config.title,
            "description": config.description,
            "deadlineInfo": config.deadline_info,
        }
