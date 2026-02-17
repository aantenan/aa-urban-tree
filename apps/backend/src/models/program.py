"""Pydantic models for public program configuration (program details, resources, metadata)."""
from typing import Any

from pydantic import BaseModel, Field


class ResourceItem(BaseModel):
    """A single downloadable resource (PDF, template, guideline)."""
    id: str = Field(description="Unique identifier for the resource")
    label: str = Field(description="Display name")
    description: str | None = None
    storage_key: str | None = Field(default=None, description="Storage key for file serving")
    url: str | None = Field(default=None, description="Optional direct URL")
    file_type: str | None = Field(default=None, description="File type e.g. PDF")
    title: str | None = Field(default=None, description="Alternative to label for API compatibility")


class ProgramMetadata(BaseModel):
    """Metadata for program info (e.g. last updated, version)."""
    last_updated: str | None = None
    version: str | None = None


class GrantCycle(BaseModel):
    """Grant cycle dates."""
    year: int | None = None
    application_open: str | None = Field(default=None, description="ISO 8601 date")
    application_deadline: str | None = Field(default=None, description="ISO 8601 date")
    award_notification_date: str | None = Field(default=None, description="ISO 8601 date")


class FundingLimits(BaseModel):
    """Funding limits in dollars."""
    minimum: float | None = None
    maximum: float | None = None


class EligibilityConfig(BaseModel):
    """Structured eligibility criteria."""
    applicant_types: list[str] = Field(default_factory=list)
    project_types: list[str] = Field(default_factory=list)
    funding_limits: FundingLimits | None = None
    cost_match_requirement: float | None = Field(default=None, description="Cost match percentage")
    ineligible_activities: list[str] = Field(default_factory=list)
    summary: str | None = Field(default=None, description="Plain text summary for backward compat")


class ProgramInfo(BaseModel):
    """Program information section."""
    name: str | None = Field(default=None, description="Program name")
    purpose: str | None = None
    funding_available: float | None = None
    contact_email: str | None = None
    contact_phone: str | None = None


class ProgramConfig(BaseModel):
    """Program information served by the public configuration API."""
    title: str = Field(description="Program title")
    description: str = Field(default="", description="Program description")
    eligibility: str | None = None
    deadline_info: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    resources: list[ResourceItem] = Field(default_factory=list)
    metadata: ProgramMetadata | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
    # Extended structure for /api/config/program
    program: ProgramInfo | None = None
    grant_cycle: GrantCycle | None = None
    eligibility_config: EligibilityConfig | None = None
