import json

import pytest

import storage
from schemas import OwnedSystem


def test_owned_system_contract_accepts_registered_inventory_shape():
    record = json.loads(storage.OWNED_SYSTEM_SEED_PATH.read_text(encoding="utf-8"))[0]

    assert record["name"] == record["system_name"]
    assert record["capabilities"]
    rich_only_record = {
        key: value for key, value in record.items() if key not in {"name", "capabilities"}
    }
    system = OwnedSystem.model_validate(rich_only_record)

    assert system.name == "SAP S/4HANA"
    assert "decide or approve" in system.capabilities
    assert "financial" in system.capabilities


def test_hosted_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        storage._database_url()
