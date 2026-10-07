"""Engine 2: apply the decision-output rules, with legacy interview helpers."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv

from decision_rules import build_decision_portfolio
from reconcile import reconcile_answers
from schemas import (
    Band, Cluster, InterviewAnswer, Judgment, Recommendation, Reconciliation, Verdict,
)

CONFIDENCE_THRESHOLD = 0.75

# Load the visible local key file first, then allow .env/environment overrides.
load_dotenv(Path(__file__).with_name("api_key.env"))
load_dotenv(override=True)

REQUIRED_EVIDENCE = {
    "process owner": ("owner", "owns", "responsible"),
    "current workflow": ("workflow", "process", "handoff", "steps"),
    "source of truth": ("data", "stored", "system", "source of truth"),
}


class Judge(Protocol):
    def judge(self, cluster: Cluster, evidence: Reconciliation | None = None) -> Judgment: ...


class RuleBasedJudge:
    """Stable demo fallback used when OpenAI is unavailable."""

    def judge(self, cluster: Cluster, evidence: Reconciliation | None = None) -> Judgment:
        systems = cluster.owned_system_candidates
        has_evidence = bool(evidence and evidence.evidence)
        conflict_count = len(evidence.conflicts) if evidence else 0
        value = cluster.value_band if cluster.value_band != Band.UNKNOWN else Band.MEDIUM
        effort = cluster.effort_or_cost_band if cluster.effort_or_cost_band != Band.UNKNOWN else Band.MEDIUM

        if conflict_count:
            verdict, confidence = Verdict.REDESIGN, 0.78
            reason = "Stakeholder disagreement shows the process must be aligned before technology is selected."
        elif systems and has_evidence:
            verdict, confidence = Verdict.CONSOLIDATE, 0.86
            reason = f"The need can be met by enabling or consolidating capabilities in {', '.join(systems)}."
        elif systems:
            verdict, confidence = Verdict.REDESIGN, 0.68
            reason = f"Existing systems ({', '.join(systems)}) may cover the need, but the operating process is unclear."
        elif has_evidence:
            verdict, confidence = Verdict.BUY, 0.80
            reason = "The need is evidenced and no plausible owned-system capability was identified."
        else:
            verdict, confidence = Verdict.INVESTIGATE, 0.55
            reason = "There is not enough operational evidence to make a responsible build-or-buy decision."

        return Judgment(
            verdict=verdict, reasoning=reason, confidence=confidence,
            value_band=value, effort_or_cost_band=effort,
            missing_evidence=[] if has_evidence else list(cluster.missing_information),
        )


class OpenAIJudge:
    """OpenAI structured-output judge."""

    def __init__(self, model: str | None = None):
        from openai import OpenAI

        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-6-astra")

    def judge(self, cluster: Cluster, evidence: Reconciliation | None = None) -> Judgment:
        prompt = {
            "task": "Judge one AI transformation cluster. Be conservative when evidence is absent.",
            "allowed_verdicts": [v.value for v in Verdict],
            "cluster": cluster.model_dump(mode="json"),
            "stakeholder_evidence": evidence.model_dump(mode="json") if evidence else None,
        }
        completion = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Return a conservative judgment that follows the supplied schema.",
                },
                {"role": "user", "content": json.dumps(prompt)},
            ],
            response_format=Judgment,
        )
        judgment = completion.choices[0].message.parsed
        if judgment is None:
            refusal = completion.choices[0].message.refusal
            raise RuntimeError(refusal or "OpenAI returned no structured judgment.")
        return judgment


def get_judge() -> Judge:
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return OpenAIJudge()
        except Exception:
            pass
    return RuleBasedJudge()


def evidence_gate(cluster: Cluster, judgment: Judgment) -> list[str]:
    """Return missing facts. An empty list means the decision can proceed."""
    missing = list(dict.fromkeys(cluster.missing_information + judgment.missing_evidence))
    searchable = " ".join([cluster.underlying_need, *missing]).lower()
    for label, keywords in REQUIRED_EVIDENCE.items():
        if not any(keyword in searchable for keyword in keywords):
            missing.append(label)
    if judgment.confidence < CONFIDENCE_THRESHOLD and not missing:
        missing.append("evidence supporting the confidence score")
    return list(dict.fromkeys(missing))


def generate_questions(missing_evidence: list[str], limit: int = 5) -> list[str]:
    templates = {
        "process owner": "Who owns this process and who approves changes to it?",
        "current workflow": "Walk me through the current workflow, including its handoffs.",
        "source of truth": "Which system is the source of truth, and who keeps it current?",
    }
    questions = []
    for item in missing_evidence:
        key = item.lower().strip(" ?." )
        questions.append(templates.get(key, f"What is the current evidence for: {item.rstrip('?.')}?"))
    questions = list(dict.fromkeys(questions))
    if len(questions) == 1:
        questions.append("What happens when this information is missing, late, or disputed?")
    return questions[: max(2, min(limit, 5))]


def assemble_recommendation(
    cluster: Cluster, judgment: Judgment, reconciliation: Reconciliation | None = None
) -> Recommendation:
    reconciliation = reconciliation or Reconciliation()
    traces = [entry for entries in reconciliation.evidence.values() for entry in entries]
    if not traces:
        traces = [f"Engine 1: underlying need is '{cluster.underlying_need}'."]
    conflicts = [f"{c.topic}: {c.explanation}" for c in reconciliation.conflicts]
    actions = {
        Verdict.INVESTIGATE: "Collect the missing evidence and reconvene the decision owners.",
        Verdict.REDESIGN: "Align owners on one target process before selecting or configuring technology.",
        Verdict.CONSOLIDATE: f"Pilot the capability in {cluster.owned_system_candidates[0] if cluster.owned_system_candidates else 'an owned platform'}.",
        Verdict.BUILD: "Prototype the smallest differentiating workflow and validate it with users.",
        Verdict.BUY: "Run a requirements-led vendor evaluation with a time-boxed proof of value.",
        Verdict.AVOID: "Do not fund this initiative; document the decision and review only if evidence changes.",
    }
    return Recommendation(
        cluster_id=cluster.cluster_id, cluster_name=cluster.cluster_name,
        verdict=judgment.verdict, confidence=judgment.confidence,
        rationale=judgment.reasoning, next_action=actions[judgment.verdict],
        evidence_trace=traces, conflicts=conflicts,
    )


def run_engine2(cluster: Cluster, interviews: list[InterviewAnswer] | None = None) -> tuple[Judgment, list[str], Reconciliation, Recommendation]:
    judge = get_judge()
    initial = judge.judge(cluster)
    missing = evidence_gate(cluster, initial)
    reconciliation = reconcile_answers(interviews or [])
    final = judge.judge(cluster, reconciliation) if interviews else initial
    if interviews:
        missing = []
    return final, missing, reconciliation, assemble_recommendation(cluster, final, reconciliation)
