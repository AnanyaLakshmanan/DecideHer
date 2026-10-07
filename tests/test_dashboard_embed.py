import json

from scripts.dashboard_embed import build_embedded_dashboard
from scripts.dashboard_export import DASHBOARD_DATA_PATH


def test_dashboard_embed_inlines_bundle_and_current_payload():
    existed = DASHBOARD_DATA_PATH.exists()
    original = DASHBOARD_DATA_PATH.read_text(encoding="utf-8") if existed else None
    try:
        payload = {
            "initiatives": [],
            "departments": [],
            "blockers": [],
            "metrics": {"reports": 987},
            "advisorKnowledgeBase": {},
        }
        DASHBOARD_DATA_PATH.write_text(json.dumps(payload), encoding="utf-8")

        document = build_embedded_dashboard("dashboard")

        assert "window.__DECIDEHER_VIEW__=\"dashboard\"" in document
        assert '"reports":987' in document
        assert '<script type="module" crossorigin src=' not in document
        assert '<link rel="stylesheet" crossorigin href=' not in document
        assert "window.__DECIDEHER_DASHBOARD__" in document
    finally:
        if original is not None:
            DASHBOARD_DATA_PATH.write_text(original, encoding="utf-8")
        elif DASHBOARD_DATA_PATH.exists():
            DASHBOARD_DATA_PATH.unlink()
