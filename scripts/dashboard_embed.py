"""Create a self-contained dashboard document for Streamlit's iframe."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal

from scripts.dashboard_export import DASHBOARD_DATA_PATH, DASHBOARD_DIRECTORY

_SCRIPT_PATTERN = re.compile(
    r'<script\s+type="module"\s+crossorigin\s+src="(?P<src>[^"]+)"></script>'
)
_STYLE_PATTERN = re.compile(
    r'<link\s+rel="stylesheet"\s+crossorigin\s+href="(?P<href>[^"]+)">'
)


def _asset_text(reference: str) -> str:
    """Read one Vite asset while preventing paths outside the dashboard build."""
    build_root = DASHBOARD_DIRECTORY.resolve()
    asset_path = (DASHBOARD_DIRECTORY / reference).resolve()
    if asset_path != build_root and build_root not in asset_path.parents:
        raise ValueError(f"Dashboard asset is outside the build directory: {reference}")
    return asset_path.read_text(encoding="utf-8")


def _javascript_json(value: object) -> str:
    """Serialize trusted pipeline data safely inside a script element."""
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def build_embedded_dashboard(view: Literal["home", "dashboard"]) -> str:
    """Inline the Vite bundle and current dashboard JSON for Cloud deployment."""
    index_path = DASHBOARD_DIRECTORY / "index.html"
    if not index_path.exists():
        raise FileNotFoundError(index_path)
    if not DASHBOARD_DATA_PATH.exists():
        raise FileNotFoundError(DASHBOARD_DATA_PATH)

    document = index_path.read_text(encoding="utf-8")
    script_match = _SCRIPT_PATTERN.search(document)
    style_match = _STYLE_PATTERN.search(document)
    if not script_match or not style_match:
        raise RuntimeError("The dashboard build does not contain the expected Vite assets.")

    javascript = _asset_text(script_match.group("src"))
    stylesheet = _asset_text(style_match.group("href"))
    dashboard_payload = json.loads(DASHBOARD_DATA_PATH.read_text(encoding="utf-8"))
    bootstrap = (
        "<script>"
        f"window.__DECIDEHER_VIEW__={json.dumps(view)};"
        f"window.__DECIDEHER_DASHBOARD__={_javascript_json(dashboard_payload)};"
        "</script>"
    )

    document = _STYLE_PATTERN.sub(
        lambda _match: f"<style>{stylesheet}</style>", document, count=1
    )
    document = _SCRIPT_PATTERN.sub(
        lambda _match: f'{bootstrap}<script type="module">{javascript}</script>',
        document,
        count=1,
    )
    return document
