"""Single visible input screen; submission runs Engine 1 before output."""
import streamlit as st
from pydantic import ValidationError

from engine1 import derive_issue_fields, validate_meaningful_submission
from form_loader import render_intake_form
from pipeline import cluster_database
from schemas import IssueSubmission
from storage import persist_submission
from ui_navigation import TOP_NAVIGATION_CSS, navigation_html

st.html(
    """
    <style>
      __TOP_NAVIGATION_CSS__

      [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 92% 4%, rgba(234, 88, 12, 0.09), transparent 24rem),
          #FAF8F5;
      }

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

      .stMainBlockContainer {
        width: 100% !important;
        max-width: none !important;
        padding: 0 0 4rem !important;
      }

      .intake-topbar {
        position: relative;
        z-index: 50;
        width: 100%;
        padding: 0.75rem 2rem;
        border-bottom: 1px solid #580B1B;
        color: white;
        background: #700E22;
        box-shadow: 0 4px 14px rgba(52, 7, 18, 0.2);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      .intake-topbar-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        width: 100%;
        max-width: 1780px;
        margin: 0 auto;
      }

      .intake-brand {
        display: inline-flex;
        flex: 0 0 auto;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        border: 1px solid #E7E5E4;
        border-radius: 12px;
        color: #700E22 !important;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        text-decoration: none !important;
      }

      .intake-brand-mark {
        position: relative;
        overflow: hidden;
        width: 38px;
        height: 30px;
        flex: 0 0 38px;
      }

      .intake-brand-mark img {
        position: absolute;
        top: -29px;
        left: -36px;
        width: 114px;
        max-width: none;
        height: 114px;
      }

      .intake-brand-name {
        font-size: 1.08rem;
        font-weight: 900;
        letter-spacing: -0.035em;
      }

      .intake-brand-name span {
        color: #EA580C;
      }

      .intake-nav {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: clamp(0.5rem, 0.7vw, 0.75rem);
        flex-wrap: wrap;
      }

      .intake-nav-link,
      .intake-nav-button {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        min-height: 2rem;
        padding: 0.38rem 0.75rem;
        border: 1px solid transparent;
        border-radius: 8px;
        color: rgba(255,255,255,0.92) !important;
        background: transparent;
        font-size: 0.78rem;
        font-weight: 650;
        line-height: 1;
        text-decoration: none !important;
        cursor: pointer;
      }

      .intake-nav-link svg,
      .intake-nav-button svg {
        width: 0.875rem;
        height: 0.875rem;
        flex: 0 0 auto;
        fill: none;
        stroke: currentColor;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
      }

      .intake-nav-link.is-primary svg {
        stroke: #292524;
      }

      .intake-nav-button .nav-accent-icon {
        stroke: #F5A623;
      }

      .intake-nav-button .nav-chevron {
        width: 0.75rem;
        height: 0.75rem;
        opacity: 0.8;
      }

      .intake-nav-link:hover,
      .intake-nav-button:hover,
      .intake-nav-link.is-active {
        border-color: rgba(255,255,255,0.24);
        color: white !important;
        background: rgba(255,255,255,0.15);
      }

      .intake-nav-link.is-primary {
        border-color: #D97706;
        color: #292524 !important;
        background: #F5A623;
        font-weight: 800;
      }

      .intake-nav-link.is-primary:hover {
        background: #E09612;
      }

      .intake-nav-menu {
        position: relative;
      }

      .intake-nav-popover {
        position: absolute;
        top: calc(100% + 0.45rem);
        right: 0;
        display: none;
        width: 340px;
        padding: 1rem;
        border: 1px solid #E7E5E4;
        border-radius: 14px;
        color: #44403C;
        background: white;
        box-shadow: 0 18px 45px rgba(28, 25, 23, 0.2);
        font-size: 0.78rem;
        line-height: 1.45;
      }

      .intake-nav-menu:hover .intake-nav-popover,
      .intake-nav-menu:focus-within .intake-nav-popover {
        display: block;
      }

      .intake-nav-popover strong {
        display: block;
        margin-bottom: 0.45rem;
        color: #700E22;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }

      .intake-nav-popover p {
        margin: 0.38rem 0;
      }

      .intake-page-heading {
        width: min(980px, calc(100vw - 3rem));
        margin: 0 auto;
        padding: 3rem 0 0.25rem;
        text-align: center;
      }

      .intake-page-heading h1 {
        margin: 0;
        color: #1C1917;
        font-size: clamp(2.1rem, 4vw, 3.4rem);
        line-height: 1.05;
        letter-spacing: -0.045em;
      }

      .intake-page-heading h2 {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        margin: 1.15rem 0 0.55rem;
        padding: 0.5rem 1rem;
        border: 1px solid #FBE0E5;
        border-radius: 999px;
        color: #700E22;
        background: #FDF2F4;
        font-size: 1rem;
        font-weight: 850;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      .intake-page-heading h2::before {
        content: "";
        width: 0.45rem;
        height: 0.45rem;
        border-radius: 999px;
        background: #EA580C;
      }

      .storage-note {
        display: flex;
        gap: 0.85rem;
        align-items: flex-start;
        width: min(1540px, calc(100vw - 3rem));
        margin: 1.35rem auto;
        padding: 0.9rem 1rem;
        border: 1px solid #F5D4C6;
        border-radius: 12px;
        color: #5B2118;
        background: #FFF8F6;
        font-size: 0.88rem;
        line-height: 1.5;
      }

      .storage-icon {
        flex: 0 0 auto;
        display: grid;
        place-items: center;
        width: 1.8rem;
        height: 1.8rem;
        border-radius: 9px;
        color: white;
        background: #EA580C;
        font-weight: 900;
      }

      [data-testid="stForm"] {
        width: min(1540px, calc(100vw - 3rem)) !important;
        margin: 0 auto !important;
        padding: 2rem 2.1rem 2.25rem !important;
        border: 1px solid #E9E2DE !important;
        border-radius: 18px !important;
        background: rgba(255,255,255,0.96) !important;
        box-shadow: 0 12px 35px rgba(52, 7, 18, 0.07) !important;
      }

      [data-testid="stForm"] h3 {
        margin: 0.25rem 0 0 !important;
        color: #700E22 !important;
        font-size: 1.1rem !important;
        letter-spacing: -0.01em;
      }

      .required-key {
        margin-top: -0.15rem;
        padding-top: 0;
        color: #6B625E;
        font-size: 0.88rem;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
      }

      .required-key span {
        color: #EA580C;
        font-weight: 900;
      }

      [data-testid="stForm"] hr {
        margin: 0.65rem 0 1.15rem !important;
        border-color: #F0E8E4 !important;
      }

      [data-testid="stWidgetLabel"] p {
        color: #3F3A37 !important;
        font-size: 0.9rem !important;
        font-weight: 650 !important;
      }

      [data-testid="stForm"] input,
      [data-testid="stForm"] textarea,
      [data-testid="stForm"] [role="combobox"],
      [data-testid="stForm"] [role="radiogroup"] label,
      [data-testid="stForm"] [data-testid="stCaptionContainer"] p {
        font-size: 0.88rem !important;
      }

      [data-testid="stTextInputRootElement"],
      [data-testid="stTextAreaRootElement"],
      [data-testid="stSelectbox"] div[role="group"],
      [data-testid="stMultiSelect"] div[role="group"] {
        min-height: 3.15rem !important;
        border: 1px solid #C7C2BF !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 4px rgba(52, 7, 18, 0.06) !important;
      }

      [data-testid="stTextInputRootElement"]:focus-within,
      [data-testid="stTextAreaRootElement"]:focus-within,
      [data-testid="stSelectbox"] div[role="group"]:focus-within,
      [data-testid="stMultiSelect"] div[role="group"]:focus-within {
        border-color: #700E22 !important;
        box-shadow: 0 0 0 2px rgba(112, 14, 34, 0.12), 0 2px 7px rgba(52, 7, 18, 0.07) !important;
      }

      [data-testid="stTextArea"] textarea {
        min-height: 7.5rem !important;
        background: transparent !important;
      }

      [data-testid="stTextInput"] input,
      [data-testid="stSelectbox"] input,
      [data-testid="stMultiSelect"] input {
        min-height: 3rem !important;
        background: transparent !important;
      }

      [data-testid="stFormSubmitButton"] button {
        width: 100% !important;
        min-height: 3rem !important;
        margin-top: 0.75rem !important;
        border: 1px solid #4D0A18 !important;
        border-radius: 11px !important;
        color: white !important;
        background: #700E22 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 7px 18px rgba(112, 14, 34, 0.2) !important;
      }

      [data-testid="stFormSubmitButton"] button:hover {
        border-color: #EA580C !important;
        background: #580B1B !important;
      }

      @media (max-width: 700px) {
        .stMainBlockContainer {
          padding: 0 0 2.5rem !important;
        }
        .intake-topbar { padding: 0.65rem 0.75rem; }
        .intake-topbar-inner { align-items: flex-start; flex-direction: column; }
        .intake-nav { justify-content: flex-start; }
        .intake-nav-popover { left: 0; right: auto; width: min(340px, calc(100vw - 1.5rem)); }
        .intake-page-heading,
        .storage-note,
        [data-testid="stForm"] { width: calc(100vw - 1.2rem) !important; }
        .intake-page-heading { padding-top: 2rem; }
        [data-testid="stForm"] { padding: 1.1rem 1rem 1.3rem !important; }
      }

      @media (max-width: 520px) {
        .intake-page-heading h1 { font-size: 2rem; }
      }
    </style>

    __TOP_NAVIGATION__

    <section class="intake-page-heading">
      <h1>Turning AI Ideas in Action</h1>
      <h2>Employee Idea Input Form</h2>
    </section>

    <div class="storage-note">
      <span class="storage-icon">✓</span>
      <span><strong>Your submission is stored online.</strong> Form responses are saved to the hosted DecideHer database.</span>
    </div>
    """.replace("__TOP_NAVIGATION_CSS__", TOP_NAVIGATION_CSS).replace(
        "__TOP_NAVIGATION__", navigation_html("input")
    )
)

values = render_intake_form()
if values:
    try:
        submission = IssueSubmission.model_validate(values)
        validate_meaningful_submission(submission)
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
        issue_id, storage_backend = persist_submission(
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
        clusters, selected_cluster_id = cluster_database(issue_id)
        st.session_state["clusters"] = clusters
        st.session_state["selected_cluster_id"] = selected_cluster_id
        st.session_state["interviews_by_cluster"] = {}
        st.session_state["pipeline_complete_engine1"] = True
        st.session_state["submission_reference"] = f"DH-{issue_id.split('-')[0].upper()}"
        st.session_state["storage_backend"] = storage_backend
        st.switch_page("pages/3_decision.py")
    except (ValidationError, ValueError, RuntimeError) as exc:
        st.error("Please correct the form before submitting.")
        st.code(str(exc))
