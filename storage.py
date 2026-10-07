"""PostgreSQL storage whose columns are defined by the repository CSV contracts."""
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).parent
FORM_FIELDS_PATH = ROOT / "data" / "form_fields.csv"
OWNED_SYSTEM_FIELDS_PATH = ROOT / "data" / "owned_systems.csv"
OWNED_SYSTEM_SEED_PATH = ROOT / "data" / "owned_systems.json"
DECISION_OUTPUT_FIELDS_PATH = ROOT / "data" / "decision_output_fields.csv"


def _definition(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        fields = list(csv.DictReader(source))
    for field in fields:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field["field_name"]):
            raise ValueError(f"Unsafe field name: {field['field_name']}")
    return fields


def _issue_derived_fields() -> list[str]:
    supported = {
        "root_cause_derived", "capability_type", "data_object",
        "personal_data_flag", "volume_proxy", "reach_score",
    }
    return [
        field["field_name"]
        for field in _definition(DECISION_OUTPUT_FIELDS_PATH)
        if field["sits_on"] == "issue" and field["field_name"] in supported
    ]


DERIVED_FIELDS = _issue_derived_fields()
FORM_DEFINITION = _definition(FORM_FIELDS_PATH)
FORM_FIELD_NAMES = [field["field_name"] for field in FORM_DEFINITION]
LIST_FIELDS = {
    field["field_name"] for field in FORM_DEFINITION if field["input_type"] == "multi-select"
}
OWNED_SYSTEM_DEFINITION = _definition(OWNED_SYSTEM_FIELDS_PATH)
OWNED_SYSTEM_FIELD_NAMES = [field["field_name"] for field in OWNED_SYSTEM_DEFINITION]
OWNED_SYSTEM_LIST_FIELDS = {
    field["field_name"] for field in OWNED_SYSTEM_DEFINITION
    if field["input_type"] == "multi-select"
}


def _issues_schema() -> str:
    form_columns = ",\n".join(f'"{name}" TEXT' for name in FORM_FIELD_NAMES)
    derived_columns = ",\n".join(f'"{name}" TEXT' for name in DERIVED_FIELDS)
    return f"""CREATE TABLE IF NOT EXISTS issues (
        issue_id TEXT PRIMARY KEY,
        {form_columns},
        {derived_columns},
        model_text TEXT NOT NULL,
        pipeline_status TEXT NOT NULL,
        cluster_id TEXT,
        created_at TIMESTAMPTZ NOT NULL
    )"""


def _owned_systems_schema() -> str:
    columns = ",\n".join(
        f'"{name}" TEXT' if name != "system_id" else '"system_id" TEXT PRIMARY KEY'
        for name in OWNED_SYSTEM_FIELD_NAMES
    )
    return f"""CREATE TABLE IF NOT EXISTS owned_systems (
        {columns},
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL
    )"""


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required. Add your hosted PostgreSQL pooled connection string."
        )
    return database_url


def _connect() -> psycopg.Connection:
    connection = psycopg.connect(_database_url(), row_factory=dict_row)
    connection.execute(_issues_schema())
    connection.execute(
        """CREATE TABLE IF NOT EXISTS clusters (
            cluster_id TEXT PRIMARY KEY,
            pipeline_status TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            engine1_output_json TEXT NOT NULL,
            engine2_output_json TEXT
        )"""
    )
    connection.execute(_owned_systems_schema())
    _seed_owned_systems(connection)
    connection.commit()
    return connection


def _encode(field: str, value: Any, list_fields: set[str]) -> Any:
    return json.dumps(value or []) if field in list_fields else value


def _insert_owned_system(
    connection: psycopg.Connection,
    record: dict[str, Any],
    *, created_at: datetime, updated_at: datetime,
) -> None:
    columns = [*OWNED_SYSTEM_FIELD_NAMES, "created_at", "updated_at"]
    values = [
        *[_encode(field, record.get(field), OWNED_SYSTEM_LIST_FIELDS)
          for field in OWNED_SYSTEM_FIELD_NAMES],
        created_at,
        updated_at,
    ]
    quoted = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join("%s" for _ in columns)
    updates = ", ".join(
        f'"{column}" = EXCLUDED."{column}"'
        for column in [*OWNED_SYSTEM_FIELD_NAMES[1:], "updated_at"]
    )
    connection.execute(
        f"INSERT INTO owned_systems ({quoted}) VALUES ({placeholders}) "
        f"ON CONFLICT (system_id) DO UPDATE SET {updates}",
        values,
    )


def _seed_owned_systems(connection: psycopg.Connection) -> None:
    count = connection.execute("SELECT COUNT(*) AS count FROM owned_systems").fetchone()["count"]
    if count:
        return
    now = datetime.now(timezone.utc)
    for record in json.loads(OWNED_SYSTEM_SEED_PATH.read_text(encoding="utf-8")):
        _insert_owned_system(connection, record, created_at=now, updated_at=now)


def _insert_issue(
    connection: psycopg.Connection,
    *, issue_id: str, answers: dict[str, Any], derived: dict[str, Any],
    model_text: str, pipeline_status: str, cluster_id: str | None,
    created_at: datetime, ignore_existing: bool = False,
) -> psycopg.Cursor:
    columns = [
        "issue_id", *FORM_FIELD_NAMES, *DERIVED_FIELDS,
        "model_text", "pipeline_status", "cluster_id", "created_at",
    ]
    values = [
        issue_id,
        *[_encode(field, answers.get(field), LIST_FIELDS) for field in FORM_FIELD_NAMES],
        *[derived.get(field) for field in DERIVED_FIELDS],
        model_text, pipeline_status, cluster_id, created_at,
    ]
    quoted = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join("%s" for _ in columns)
    conflict = " ON CONFLICT (issue_id) DO NOTHING" if ignore_existing else ""
    return connection.execute(
        f"INSERT INTO issues ({quoted}) VALUES ({placeholders}){conflict}", values
    )


def next_owned_system_id() -> str:
    with _connect() as connection:
        rows = connection.execute("SELECT system_id FROM owned_systems").fetchall()
    numbers = [
        int(match.group(1)) for row in rows
        if (match := re.fullmatch(r"SYS-(\d+)", str(row["system_id"])))
    ]
    return f"SYS-{max(numbers, default=0) + 1:03d}"


def list_owned_systems() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM owned_systems ORDER BY system_id").fetchall()
    systems = []
    for row in rows:
        record = dict(row)
        for field in OWNED_SYSTEM_LIST_FIELDS:
            record[field] = json.loads(record.get(field) or "[]")
        systems.append(record)
    return systems


def persist_owned_system(record: dict[str, Any]) -> str:
    normalized = {
        field: record.get(field, [] if field in OWNED_SYSTEM_LIST_FIELDS else "")
        for field in OWNED_SYSTEM_FIELD_NAMES
    }
    normalized["system_id"] = str(normalized.get("system_id") or next_owned_system_id())
    missing = [
        field["question"] or field["field_name"] for field in OWNED_SYSTEM_DEFINITION
        if field["required"] == "yes" and not normalized.get(field["field_name"])
    ]
    if missing:
        raise ValueError("Please complete: " + ", ".join(missing))
    now = datetime.now(timezone.utc)
    with _connect() as connection:
        existing = connection.execute(
            "SELECT created_at FROM owned_systems WHERE system_id = %s",
            (normalized["system_id"],),
        ).fetchone()
        _insert_owned_system(
            connection, normalized,
            created_at=existing["created_at"] if existing else now, updated_at=now,
        )
    return normalized["system_id"]


def persist_submission(
    *, submitter: dict[str, str], issue: dict[str, Any],
    derived: dict[str, Any], model_text: str,
) -> tuple[str, str]:
    issue_id = str(uuid4())
    with _connect() as connection:
        _insert_issue(
            connection, issue_id=issue_id, answers={**issue, **submitter},
            derived=derived, model_text=model_text, pipeline_status="submitted",
            cluster_id=None, created_at=datetime.now(timezone.utc),
        )
    return issue_id, "Hosted PostgreSQL"


def persist_sample_submission(
    sample_key: str, *, submitter: dict[str, str], issue: dict[str, Any],
    derived: dict[str, Any], model_text: str,
) -> bool:
    issue_id = str(uuid5(NAMESPACE_URL, f"decideher:sample:issue:{sample_key}"))
    answers = {**issue, **submitter}
    with _connect() as connection:
        cursor = _insert_issue(
            connection, issue_id=issue_id, answers=answers, derived=derived,
            model_text=model_text, pipeline_status="submitted", cluster_id=None,
            created_at=datetime.now(timezone.utc), ignore_existing=True,
        )
        inserted = cursor.rowcount == 1
        if not inserted:
            fields = [*FORM_FIELD_NAMES, *DERIVED_FIELDS, "model_text"]
            values = [
                *[_encode(field, answers.get(field), LIST_FIELDS) for field in FORM_FIELD_NAMES],
                *[derived.get(field) for field in DERIVED_FIELDS], model_text, issue_id,
            ]
            assignments = ", ".join(f'"{field}" = %s' for field in fields)
            connection.execute(f"UPDATE issues SET {assignments} WHERE issue_id = %s", values)
    return inserted


def reset_database_records() -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM clusters")
        connection.execute("DELETE FROM issues")


def count_records() -> tuple[int, int]:
    with _connect() as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM issues").fetchone()["count"]
    return count, count


def _decoded_answers(row: dict[str, Any]) -> dict[str, Any]:
    answers = {}
    for field in FORM_FIELD_NAMES:
        value = row[field]
        if field in LIST_FIELDS:
            value = json.loads(value or "[]")
            if isinstance(value, str) and value.startswith("["):
                value = json.loads(value)
        answers[field] = value
    return answers


def fetch_issues_for_engine1() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM issues ORDER BY created_at").fetchall()
    return [
        {**dict(row), "payload": _decoded_answers(row),
         "derived": {field: row[field] for field in DERIVED_FIELDS}}
        for row in rows
    ]


def replace_engine1_clusters(clusters: list[dict[str, Any]], assignments: dict[str, str]) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM clusters")
        for cluster in clusters:
            connection.execute(
                "INSERT INTO clusters VALUES (%s, %s, %s, %s, %s)",
                (cluster["cluster_id"], "engine1_complete", datetime.now(timezone.utc),
                 json.dumps(cluster), None),
            )
        for issue_id, cluster_id in assignments.items():
            connection.execute(
                "UPDATE issues SET pipeline_status = 'clustered', cluster_id = %s WHERE issue_id = %s",
                (cluster_id, issue_id),
            )


def list_engine1_clusters() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT engine1_output_json FROM clusters ORDER BY cluster_id"
        ).fetchall()
    return [json.loads(row["engine1_output_json"]) for row in rows]


def save_engine2_outputs(initiatives: list[dict[str, Any]]) -> None:
    with _connect() as connection:
        for initiative in initiatives:
            connection.execute(
                "UPDATE clusters SET pipeline_status = %s, engine2_output_json = %s WHERE cluster_id = %s",
                ("engine2_complete", json.dumps(initiative), f"C{initiative['id']}"),
            )


def mark_issue_clustered(issue_id: str, cluster_id: str) -> None:
    with _connect() as connection:
        cursor = connection.execute(
            "UPDATE issues SET pipeline_status = 'clustered', cluster_id = %s WHERE issue_id = %s",
            (cluster_id, issue_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Issue not found: {issue_id}")
