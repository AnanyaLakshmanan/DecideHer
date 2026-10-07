import json

import sample_data


def test_samples_keep_original_submitter_data():
    records = json.loads(sample_data.SAMPLE_PATH.read_text())

    assert records[0]["name"]
    assert "@" in records[0]["email"]
    assert not records[0]["name"].startswith("[")


def test_samples_cover_problem_types_and_departments():
    records = json.loads(sample_data.SAMPLE_PATH.read_text())

    assert len(records) >= 20
    assert {record["root_cause_stated"] for record in records} == {
        "The people involved",
        "The process itself",
        "The technology",
        "The data",
    }
    assert len({record["department"] for record in records}) >= 8
    assert len({record["task_type"] for record in records}) >= 7
