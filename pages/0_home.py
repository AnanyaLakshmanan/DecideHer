"""Render the integrated React home page and prepare its live pipeline summary."""
from pathlib import Path

import streamlit as st

from scripts.dashboard_embed import build_embedded_dashboard
from scripts.dashboard_export import DASHBOARD_DATA_PATH
from pipeline import cluster_database


def _prepare_dashboard_data() -> None:
    """Run the same hosted-data pipeline used after form submission."""
    clusters, _ = cluster_database()
    st.session_state["clusters"] = clusters
    st.session_state["interviews_by_cluster"] = {}
    st.session_state["pipeline_complete_engine1"] = True


if not st.session_state.get("pipeline_complete_engine1") or not DASHBOARD_DATA_PATH.exists():
    try:
        _prepare_dashboard_data()
    except Exception as exc:  # Keep a useful failure state on hosted deployments.
        st.error("The DecideHer pipeline could not prepare the home-page summary.")
        st.code(str(exc))
        st.stop()

built_dashboard = Path(__file__).parents[1] / "static" / "dashboard" / "index.html"
if not built_dashboard.exists():
    st.error("The DecideHer frontend has not been built. Run `cd frontend && npm run build`.")
    st.stop()

st.html(
    """
    <style>
      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stAppToolbar"],
      [data-testid="stElementToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"],
      #MainMenu,
      footer {
        display: none !important;
      }

      [data-testid="stAppViewContainer"],
      [data-testid="stMain"],
      .stMainBlockContainer,
      [data-testid="stVerticalBlock"] {
        height: 100vh !important;
        min-height: 100vh !important;
        overflow: hidden !important;
      }

      [data-testid="stAppViewContainer"],
      [data-testid="stMain"] {
        background: #FAF8F5 !important;
      }

      .stMainBlockContainer {
        width: 100% !important;
        max-width: none !important;
        padding: 0 !important;
      }

      [data-testid="stVerticalBlock"] {
        gap: 0 !important;
      }

      [data-testid="stIFrame"],
      [data-testid="stIFrame"] iframe {
        width: 100% !important;
        height: 100vh !important;
        border: 0 !important;
        display: block !important;
      }
    </style>
    """
)
st.iframe(
    build_embedded_dashboard("home"),
    width="stretch",
    height="stretch",
    tab_index=0,
)
