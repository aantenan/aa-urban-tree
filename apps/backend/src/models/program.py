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


class ProgramMetadata(BaseModel):
    """Metadata for program info (e.g. last updated, version)."""
    last_updated: str | None = None
    version: str | None = None


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
