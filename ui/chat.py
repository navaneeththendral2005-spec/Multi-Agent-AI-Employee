"""
Chat workspace: landing screen, message thread, and execution details.

All execution still goes through MultiAgentWorkflow via the status helper.
"""

from datetime import datetime
from html import escape

import streamlit as st

from ui.agents import agent_label
from ui.file_upload import render_composer_upload

SUGGESTIONS = [
    {
        "title": "Research briefing",
        "desc": "Latest AI developments in a structured summary",
        "prompt": "Research the latest breakthroughs and market trends in artificial intelligence. Provide a structured executive summary with key takeaways.",
    },
    {
        "title": "API backend",
        "desc": "FastAPI service with auth and CRUD",
        "prompt": "Build a modular FastAPI backend structure with JWT authentication, SQLite/PostgreSQL models, and CRUD endpoints.",
    },
    {
        "title": "Data analysis",
        "desc": "Metrics, distributions, and recommendations",
        "prompt": "Analyze dataset files, calculate descriptive statistics and distributions, and generate an actionable analytical report.",
    },
    {
        "title": "Stakeholder email",
        "desc": "Milestone update and next deliverables",
        "prompt": "Draft a polished, professional email update to project stakeholders summarizing completed milestones, ongoing tasks, and next deliverables.",
    },
]


def render_workspace_bar(agent_count: int, processing: bool) -> None:
    """Top bar with workspace name and live status."""
    status_class = "live" if processing else ""
    status_label = "Processing request" if processing else "Ready"
    st.markdown(
        f"""
        <div class="workspace-bar">
            <div class="workspace-title">Workspace</div>
            <div class="workspace-meta">
                <span class="status-pill {status_class}">
                    <span class="pulse"></span>
                    {status_label}
                </span>
                <span class="status-pill">{agent_count} registered agents</span>
                <span>Orchestrator online</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_landing() -> str | None:
    """Empty-state composer."""
    st.markdown(
        """
        <div class="hero">
            <h1>Hello, what can I do for you today?</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([0.06, 0.88, 0.06])

    with center:
        submitted_text = render_request_composer(
            form_key="workspace_request_form",
            text_key="landing_text_input",
            upload_key_suffix="landing",
            placeholder="Message your AI Employee",
        )

    return submitted_text


def render_request_composer(
    form_key: str,
    text_key: str,
    upload_key_suffix: str,
    placeholder: str,
) -> str | None:
    """Render the shared glass request composer."""
    submitted_text = None

    with st.form(key=form_key, clear_on_submit=True):
        user_text = st.text_area(
            label="Task",
            placeholder=placeholder,
            label_visibility="collapsed",
            height=116,
            key=text_key,
        )
        spacer, upload, button = st.columns([0.52, 0.28, 0.20], gap="small")
        with spacer:
            st.markdown('<div class="composer-empty"></div>', unsafe_allow_html=True)
        with upload:
            render_composer_upload(upload_key_suffix)
        with button:
            submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_text.strip():
            submitted_text = user_text.strip()

    return submitted_text


def render_messages(messages: list) -> None:
    """Render the conversation thread."""
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for message in messages:
        if message.get("role") == "user":
            _render_user_message(message)
        else:
            _render_ai_message(message)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_user_message(message: dict) -> None:
    content = escape(str(message.get("content", "")))
    timestamp = escape(str(message.get("timestamp", "")))
    files = message.get("files") or []
    chips = ""
    if files:
        pills = "".join(
            f'<span class="attach-pill">{escape(str(name))}</span>' for name in files
        )
        chips = f'<div class="attach-row">{pills}</div>'

    st.markdown(
        f"""
        <div class="user-row">
            <div>
                <div class="msg-meta" style="text-align:right;">You · {timestamp}</div>
                <div class="user-bubble">{content}{chips}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_ai_message(message: dict) -> None:
    timestamp = escape(str(message.get("timestamp", "")))
    col_avatar, col_content = st.columns([0.07, 0.93], gap="small")
    with col_avatar:
        st.markdown('<div class="ai-avatar">AI</div>', unsafe_allow_html=True)
    with col_content:
        st.markdown(
            f'<div class="msg-meta">AI Employee · {timestamp}</div>',
            unsafe_allow_html=True,
        )
        content = message.get("content") or ""
        if message.get("error"):
            st.markdown(
                f"""
                <div class="error-card">
                    <h4>The workflow could not finish</h4>
                    <p>{escape(content)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(content)

        pipeline = message.get("pipeline") or []
        if pipeline:
            _render_pipeline_summary(pipeline)

        if message.get("execution_plan") or message.get("results"):
            _render_execution_details(
                message.get("execution_plan"),
                message.get("results"),
            )


def _render_pipeline_summary(pipeline: list) -> None:
    with st.expander("Task progress", expanded=False):
        for step in pipeline:
            icon = escape(str(step.get("icon", "•")))
            text = step.get("text", "")
            st.markdown(f"{icon} {text}")


def _render_execution_details(execution_plan: dict | None, results: dict | None) -> None:
    with st.expander("Agent plan and outputs", expanded=False):
        if execution_plan:
            tasks = execution_plan.get("tasks") or []
            if tasks:
                st.markdown("**Manager execution plan**")
                for task in tasks:
                    agent = agent_label(str(task.get("agent", "?")))
                    desc = escape(str(task.get("task", "")))
                    deps = task.get("depends_on") or []
                    deps_html = (
                        f" <span style='color:var(--text-muted)'>(after {escape(', '.join(deps))})</span>"
                        if deps
                        else ""
                    )
                    st.markdown(
                        f"""
                        <div class="plan-row">
                            <span class="plan-pill">{escape(agent)}</span>
                            <span>{desc}{deps_html}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if results:
            st.markdown("**Per-agent output**")
            for task_id, output in results.items():
                with st.expander(str(task_id), expanded=False):
                    st.markdown(str(output))


def get_timestamp() -> str:
    return datetime.now().strftime("%I:%M %p")
