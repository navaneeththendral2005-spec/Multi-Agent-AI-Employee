"""
Multi-Agent AI Employee — Streamlit workspace.

Entry point:
    streamlit run app.py

This file only handles presentation and session state. All work is executed
by the existing MultiAgentWorkflow in main.py. Agents, tools, providers,
and environment configuration are not modified here.
"""

import streamlit as st

from main import MultiAgentWorkflow
from ui.agents import agent_label
from ui.chat import (
    get_timestamp,
    render_landing,
    render_messages,
    render_request_composer,
    render_workspace_bar,
)
from ui.file_upload import build_augmented_request, get_attached_file_names
from ui.sidebar import render_sidebar
from ui.status import run_workflow_with_status
from ui.styles import inject_styles

st.set_page_config(
    page_title="AI Employee",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

REGISTERED_AGENT_NAMES = [
    "manager",
    "developer",
    "backend",
    "code_generator",
    "research",
    "content",
    "data",
    "document",
    "communication",
    "tester",
    "debugger",
    "code_reviewer",
    "code_fixer",
]


def _init_state() -> None:
    defaults = {
        "messages": [],
        "chat_sessions": [],
        "uploaded_files_data": [],
        "active_agents": set(),
        "completed_agents": set(),
        "processing": False,
        "pending_input": None,
        "queued_request": None,
        "preferred_agent": "auto",
        "current_session_id": None,
        "last_pipeline": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()
inject_styles("dark")


@st.cache_resource
def get_workflow():
    """Create and cache the backend MultiAgentWorkflow."""
    return MultiAgentWorkflow()


registered_agents = REGISTERED_AGENT_NAMES


def _apply_routing_preference(request: str) -> str:
    """Optional UI hint only. The Manager still produces the real plan."""
    preferred = st.session_state.get("preferred_agent", "auto")
    if not preferred or preferred == "auto":
        return request
    label = agent_label(preferred)
    return (
        f"Routing preference (optional): use the {label} agent when it is appropriate "
        f"for this request. If it is not a good fit, assign agents as usual.\n\n"
        f"{request}"
    )


def queue_user_request(text: str) -> None:
    """Store the user message and rerun so the thread is visible before execution."""
    if not text or not text.strip():
        st.warning("Enter a request before sending.")
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": text.strip(),
            "files": get_attached_file_names(),
            "timestamp": get_timestamp(),
        }
    )
    st.session_state.queued_request = text.strip()
    st.session_state.processing = True
    st.session_state.completed_agents = set()
    st.rerun()


def execute_queued_request() -> None:
    """Run the existing MultiAgentWorkflow for the queued request."""
    text = st.session_state.queued_request
    st.session_state.queued_request = None

    render_messages(st.session_state.messages)
    workflow = get_workflow()

    augmented_request = _apply_routing_preference(
        build_augmented_request(text)
    )
    result = run_workflow_with_status(workflow, augmented_request)

    if result:
        final_response = result.get(
            "final_response",
            "The assigned agents completed the task successfully.",
        )
        plan = result.get("execution_plan") or {}
        used = {
            str(task.get("agent", "")).lower()
            for task in plan.get("tasks", [])
            if task.get("agent")
        }
        st.session_state.completed_agents = used
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final_response,
                "execution_plan": result.get("execution_plan"),
                "results": result.get("results"),
                "pipeline": result.get("pipeline") or st.session_state.get("last_pipeline", []),
                "timestamp": get_timestamp(),
            }
        )
    else:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "I could not complete this multi-agent task. Review the error details and try again.",
                "error": True,
                "pipeline": st.session_state.get("last_pipeline", []),
                "timestamp": get_timestamp(),
            }
        )

    st.session_state.uploaded_files_data = []
    st.session_state.processing = False
    st.rerun()


render_sidebar(registered_agents)
render_workspace_bar(
    len(registered_agents),
    processing=bool(st.session_state.processing or st.session_state.queued_request),
)

if st.session_state.pending_input:
    pending = st.session_state.pending_input
    st.session_state.pending_input = None
    queue_user_request(pending)
elif st.session_state.queued_request:
    execute_queued_request()
elif not st.session_state.messages:
    central_request = render_landing()
    if central_request:
        queue_user_request(central_request)
else:
    render_messages(st.session_state.messages)
    _, center, _ = st.columns([0.06, 0.88, 0.06])
    with center:
        bottom_input = render_request_composer(
            form_key="workspace_followup_form",
            text_key="followup_text_input",
            upload_key_suffix="followup",
            placeholder="Message your AI Employee",
        )
    if bottom_input:
        queue_user_request(bottom_input)
