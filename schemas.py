"""Shared contracts at the Engine 1 -> Engine 2 seam."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UseCase(BaseModel):
    id: int
    department: str
    description: str
    value_band: str | None = None
    effort_or_cost_band: str | None = None
    capability_type: str = "extract or structure"
    data_object: str = "internal knowledge"
    departments_involved: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    blocked_by: str | None = None
    submitter_role: str | None = None
    root_cause_stated: str | None = None
    root_cause_derived: str = "Process"
    volume_proxy: int = 1
    reach_score: int = 1


class IssueSubmission(BaseModel):
    """One validated response to the intake form, before model enrichment."""
    name: str
    email: str
    department: str
    company: str
    idea: str | None = None
    what_happens_today: str
    why_we_want_this: str
    departments_involved: list[str] = Field(default_factory=list)
    summary_generated: str | None = None
    summary_confirmed: Literal["Yes, that's right", "Not quite"] | None = None
    root_cause_stated: str | None = None
    task_type: str | None = None
    frequency: str | None = None
    time_per_occurrence: str | None = None
    roles_involved: list[str] = Field(default_factory=list)
    people_affected: str | None = None
    data_used: list[str] = Field(default_factory=list)
    it_tools_used: list[str] = Field(default_factory=list)
    security_concern: list[str] = Field(default_factory=list)
    blocked_by: str | None = None
    submitter_role: str | None = None


class DerivedIssueFields(BaseModel):
    root_cause_derived: Literal["People", "Process", "Technology", "Data"]
    capability_type: str
    data_object: str
    personal_data_flag: Literal["yes", "no", "unclear"]
    volume_proxy: int = Field(ge=1, le=30)
    reach_score: int = Field(ge=1, le=5)


class OwnedSystem(BaseModel):
    """Engine-facing view of both legacy and registered owned-system records."""

    name: str
    capabilities: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_inventory_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        normalized["name"] = normalized.get("name") or normalized.get("system_name")
        if not normalized.get("capabilities"):
            combined = [
                *normalized.get("capabilities_in_use", []),
                *normalized.get("capabilities_available", []),
                *normalized.get("data_objects_held", []),
            ]
            normalized["capabilities"] = list(dict.fromkeys(combined))
        return normalized


class Engine1Cluster(BaseModel):
    cluster_id: str
    cluster_name: str
    member_use_cases: list[int]
    underlying_need: str
    owned_system_candidates: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    value_band: str = "unknown"
    effort_or_cost_band: str = "unknown"
    capability_type: str | None = None
    data_object: str | None = None
    reports_count: int = 0
    departments_count: int = 0


class Verdict(str, Enum):
    BUILD = "BUILD"
    BUY = "BUY"
    REDESIGN = "REDESIGN"
    CONSOLIDATE = "CONSOLIDATE"
    INVESTIGATE = "INVESTIGATE"
    AVOID = "AVOID"


class Band(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class Cluster(BaseModel):
    """The frozen merged shape. Unknown Engine 1 fields are preserved."""

    model_config = ConfigDict(extra="allow")

    cluster_id: str
    cluster_name: str
    member_use_cases: list[int] = Field(default_factory=list)
    underlying_need: str
    owned_system_candidates: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    verdict: Verdict | None = None
    reasoning: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    value_band: Band = Band.UNKNOWN
    effort_or_cost_band: Band = Band.UNKNOWN
    missing_evidence: list[str] = Field(default_factory=list)
    interview_required: bool = False
    questions: list[str] = Field(default_factory=list)
    next_action: str | None = None

    @field_validator("cluster_id", "cluster_name", "underlying_need")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class Judgment(BaseModel):
    verdict: Verdict
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    value_band: Band
    effort_or_cost_band: Band
    missing_evidence: list[str] = Field(default_factory=list)


class InterviewAnswer(BaseModel):
    stakeholder: str
    role: str = "Stakeholder"
    answers: dict[str, str]

    @field_validator("stakeholder")
    @classmethod
    def stakeholder_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("stakeholder must not be blank")
        return value.strip()


class Conflict(BaseModel):
    topic: str
    accounts: dict[str, str]
    explanation: str


class Reconciliation(BaseModel):
    agreements: list[str] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    evidence: dict[str, list[str]] = Field(default_factory=dict)


class Recommendation(BaseModel):
    cluster_id: str
    cluster_name: str
    verdict: Verdict
    confidence: float = Field(ge=0, le=1)
    rationale: str
    next_action: str
    evidence_trace: list[str]
    conflicts: list[str] = Field(default_factory=list)


def parse_cluster(payload: dict[str, Any]) -> Cluster:
    """Validate either the minimal Engine 1 shape or the guide's merged shape."""
    return Cluster.model_validate(payload)
