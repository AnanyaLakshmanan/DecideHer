"""Engine 1: input validation, clustering, and owned-system matching."""
import json
from pathlib import Path

from schemas import DerivedIssueFields, Engine1Cluster, IssueSubmission, OwnedSystem, UseCase

DATA_DIR = Path(__file__).parent / "data"


def load_demo_input() -> tuple[list[UseCase], list[OwnedSystem]]:
    use_cases = [UseCase.model_validate(row) for row in json.loads((DATA_DIR / "demo_use_cases.json").read_text())]
    system_rows = json.loads((DATA_DIR / "owned_systems.json").read_text())
    systems = [OwnedSystem.model_validate(row) for row in system_rows]
    return use_cases, systems


def load_fallback_clusters() -> list[Engine1Cluster]:
    rows = json.loads((DATA_DIR / "fallback_engine1.json").read_text())
    return [Engine1Cluster.model_validate(row) for row in rows]


def run_engine1(use_cases: list[UseCase], systems: list[OwnedSystem]) -> list[Engine1Cluster]:
    """Cluster on capability_type × data_object, as required by the output rules."""
    if not use_cases:
        return []
    grouped: dict[tuple[str, str], list[UseCase]] = {}
    for use_case in use_cases:
        grouped.setdefault((use_case.capability_type, use_case.data_object), []).append(use_case)

    clusters: list[Engine1Cluster] = []
    band_rank = {None: 0, "unknown": 0, "low": 1, "medium": 2, "high": 3}
    for (capability_type, data_object), members in sorted(grouped.items()):
        topic = f"{data_object.title()} · {capability_type.title()}"
        combined_text = " ".join(item.description for item in members).lower()
        system_matches = [
            system.name
            for system in systems
            if any(
                term.lower() in combined_text
                or term.lower() in capability_type
                or term.lower() in data_object
                for term in [system.name, *system.capabilities]
            )
        ]
        value_band = max((item.value_band for item in members), key=lambda value: band_rank.get(value, 0))
        effort_band = max(
            (item.effort_or_cost_band for item in members), key=lambda value: band_rank.get(value, 0)
        )
        clusters.append(
            Engine1Cluster(
                cluster_id=f"C{len(clusters) + 1}",
                cluster_name=topic,
                member_use_cases=[item.id for item in members],
                underlying_need=f"A more consistent way to {capability_type} {data_object} information",
                owned_system_candidates=system_matches,
                missing_information=[],
                value_band=value_band or "unknown",
                effort_or_cost_band=effort_band or "unknown",
                capability_type=capability_type,
                data_object=data_object,
                reports_count=len(members),
                departments_count=len({item.department for item in members}),
            )
        )
    return clusters


def validate_meaningful_submission(submission: IssueSubmission) -> None:
    """Reject placeholder text before storage, clustering, or model calls."""
    for label, value in {
        "How you do this today": submission.what_happens_today,
        "How this should work in the future": submission.why_we_want_this,
    }.items():
        words = [word for word in value.split() if any(character.isalpha() for character in word)]
        if len(words) < 4 or len(set(word.lower() for word in words)) < 3:
            raise ValueError(f"{label} needs a meaningful description of at least four words.")


def run_submission_engine1(submission: IssueSubmission, systems: list[OwnedSystem]) -> list[Engine1Cluster]:
    """Turn one intake submission into an Engine 1 cluster."""
    source_text = " ".join(
        filter(None, [submission.idea, submission.what_happens_today, submission.why_we_want_this])
    )
    searchable = f"{source_text} {' '.join(submission.it_tools_used)}".lower()
    candidates = [
        system.name
        for system in systems
        if any(term.lower() in searchable for term in [system.name, *system.capabilities])
    ]
    derived = derive_issue_fields(submission)
    missing = []
    if not submission.submitter_role:
        missing.append("process owner")
    if not submission.it_tools_used:
        missing.append("current workflow and systems used")
    if not submission.data_used:
        missing.append("source of truth")
    return [
        Engine1Cluster(
            cluster_id="C1",
            cluster_name=derived.capability_type.title(),
            member_use_cases=[1],
            underlying_need=submission.why_we_want_this or submission.idea or submission.what_happens_today,
            owned_system_candidates=candidates,
            missing_information=missing,
        )
    ]


def derive_issue_fields(submission: IssueSubmission) -> DerivedIssueFields:
    """Derive issue fields using the renamed decision-output specification."""
    text = " ".join(filter(None, [submission.idea, submission.what_happens_today, submission.why_we_want_this])).lower()
    capability = "extract or structure"
    if any(word in text for word in ("approve", "decision", "decide")):
        capability = "decide or approve"
    elif any(word in text for word in ("route", "routing", "classify", "triage")):
        capability = "classify or route"
    elif any(word in text for word in ("predict", "forecast", "score", "anomal")):
        capability = "predict or score"
    elif any(word in text for word in ("schedule", "coordinate", "calendar")):
        capability = "schedule or coordinate"
    elif any(word in text for word in ("sync", "transfer", "copy", "duplicate")):
        capability = "transfer or sync"
    elif any(word in text for word in ("summar", "brief")):
        capability = "summarise"
    elif any(word in text for word in ("find", "search", "retrieve", "answer", "lookup")):
        capability = "retrieve or answer"
    elif any(word in text for word in ("draft", "generate", "write", "create")):
        capability = "draft or generate"
    data_values = " ".join(submission.data_used).lower()
    data_object = "internal knowledge"
    if "customer" in data_values:
        data_object = "customer"
    elif "employee" in data_values or "hr" in data_values:
        data_object = "employee"
    elif "invoice" in data_values or "pricing" in data_values or "payment" in data_values:
        data_object = "financial"
    elif "order" in data_values:
        data_object = "order"
    elif "product" in data_values or "inventory" in data_values:
        data_object = "product"
    elif "supplier" in data_values or "purchas" in data_values:
        data_object = "supplier"
    elif "quality" in data_values or "audit" in data_values or "legal" in data_values:
        data_object = "quality or compliance"
    # Derive this from the problem narrative rather than copying the submitter's
    # opinion. The stated-versus-derived difference is a required portfolio finding.
    if any(phrase in text for phrase in (
        "experienced colleague", "personal experience", "tribal knowledge",
        "lack of skills", "training gap", "only one person knows",
    )):
        root_cause = "People"
    elif any(phrase in text for phrase in (
        "multiple shared", "multiple system", "combine report", "customer history",
        "inventory report", "invoice report", "spreadsheet forecast", "survey comment",
        "unusual reading", "duplicate data", "inconsistent data", "missing data",
    )):
        root_cause = "Data"
    elif any(phrase in text for phrase in (
        "legacy system", "system cannot", "system doesn't", "no integration",
        "tool limitation", "outage", "unsupported software",
    )):
        root_cause = "Technology"
    else:
        root_cause = "Process"
    concerns = set(submission.security_concern)
    personal_data = "yes" if concerns & {"Personal data of staff", "Personal data of customers"} else "unclear" if "Not sure" in concerns else "no"
    frequency_score = {
        "Several times a day": 6, "Daily": 5, "Weekly": 4, "Monthly": 3,
        "Quarterly": 2, "Yearly": 1, "Unpredictable": 2,
    }.get(submission.frequency, 1)
    time_score = {
        "Under 15 min": 1, "15-30 min": 2, "30-60 min": 3,
        "1-3 hours": 4, "3-8 hours": 5, "More than a day": 5,
    }.get(submission.time_per_occurrence, 1)
    reach_score = {
        "1": 1, "2-5": 2, "6-20": 3, "21-50": 4, "More than 50": 5,
    }.get(submission.people_affected, 1)
    return DerivedIssueFields(
        root_cause_derived=root_cause,
        capability_type=capability,
        data_object=data_object,
        personal_data_flag=personal_data,
        volume_proxy=min(30, frequency_score * time_score),
        reach_score=reach_score,
    )
