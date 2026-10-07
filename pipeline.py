"""Orchestrate Engine 1 over every intake record in hosted PostgreSQL."""
from scripts.dashboard_export import publish_dashboard
from engine1 import run_engine1
from engine2 import build_decision_portfolio
from schemas import OwnedSystem, UseCase
from storage import (
    fetch_issues_for_engine1,
    list_owned_systems,
    replace_engine1_clusters,
    save_engine2_outputs,
)


def _numeric_score(value: object, *, default: int = 1) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return {"low": 3, "medium": 10, "high": 20}.get(str(value).lower(), default)


def cluster_database(focus_issue_id: str | None = None) -> tuple[list[dict], str | None]:
    """Recluster the database, persist assignments, and locate a focused issue."""
    issues = fetch_issues_for_engine1()
    if not issues:
        replace_engine1_clusters([], {})
        publish_dashboard(build_decision_portfolio([]))
        return [], None

    use_cases = []
    for index, issue in enumerate(issues, start=1):
        derived = issue["derived"]
        volume_proxy = _numeric_score(derived.get("volume_proxy"))
        value_band = "high" if volume_proxy >= 20 else "medium" if volume_proxy >= 8 else "low"
        effort = "high" if derived.get("personal_data_flag") == "yes" else "medium"
        payload = issue["payload"]
        use_cases.append(
            UseCase(
                id=index,
                department=issue["department"],
                description=issue["model_text"],
                value_band=value_band,
                effort_or_cost_band=effort,
                capability_type=derived.get("capability_type") or "extract or structure",
                data_object=derived.get("data_object") or "internal knowledge",
                departments_involved=payload.get("departments_involved") or [],
                tools_used=payload.get("it_tools_used") or [],
                blocked_by=payload.get("blocked_by"),
                submitter_role=payload.get("submitter_role"),
                root_cause_stated=payload.get("root_cause_stated"),
                root_cause_derived=derived.get("root_cause_derived") or "Process",
                volume_proxy=volume_proxy,
                reach_score=_numeric_score(derived.get("reach_score")),
            )
        )

    systems = [OwnedSystem.model_validate(system) for system in list_owned_systems()]
    clusters = run_engine1(use_cases, systems)
    assignments = {}
    focused_cluster_id = None
    for cluster in clusters:
        for member_number in cluster.member_use_cases:
            issue_id = issues[member_number - 1]["issue_id"]
            assignments[issue_id] = cluster.cluster_id
            if issue_id == focus_issue_id:
                focused_cluster_id = cluster.cluster_id

    payloads = [cluster.model_dump(mode="json") for cluster in clusters]
    replace_engine1_clusters(payloads, assignments)
    dashboard = build_decision_portfolio(payloads)
    save_engine2_outputs(dashboard["initiatives"])
    publish_dashboard(dashboard)
    return payloads, focused_cluster_id
