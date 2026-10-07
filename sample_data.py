"""Validate and seed the representative intake records bundled with the app."""
import json
from pathlib import Path

from engine1 import derive_issue_fields
from schemas import IssueSubmission
from storage import count_records, persist_sample_submission

SAMPLE_PATH = Path(__file__).parent / "data" / "sample_submissions.json"


def seed_database() -> tuple[int, int]:
    """Ensure every bundled sample exists and return (newly added, total issues)."""
    records = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    inserted = 0
    for index, raw in enumerate(records, start=1):
        raw.setdefault(
            "summary_generated",
            f"Current: {raw['what_happens_today']} Future: {raw['why_we_want_this']}",
        )
        raw.setdefault("summary_confirmed", "Yes, that's right")
        submission = IssueSubmission.model_validate(raw)
        answers = submission.model_dump(mode="json")
        model_text = "\n".join(
            filter(
                None,
                [
                    answers.get("idea"),
                    answers.get("what_happens_today"),
                    answers.get("why_we_want_this"),
                ],
            )
        )
        inserted += persist_sample_submission(
            f"intake-{index:02d}",
            submitter={
                "name": submission.name,
                "email": submission.email,
                "company": submission.company,
                "department": submission.department,
            },
            issue=answers,
            derived=derive_issue_fields(submission).model_dump(),
            model_text=model_text,
        )
    return inserted, count_records()[1]
