"""
Sidebar navigation for the Multi-Agent AI Employee dashboard.

Preserves existing session keys used by the chat, file upload, and
workflow status components.
"""

import streamlit as st

from ui.agents import agent_icon, agent_label, agent_role


def render_sidebar(registered_agents: list) -> None:
    """Render workspace navigation, history, files, and agent roster."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-row">
                <div class="brand-mark">AI</div>
                <div>
                    <div class="brand-name">AI Employee</div>
                    <div class="brand-sub">Multi-agent workspace</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("New conversation", use_container_width=True, key="new_chat_btn"):
            _archive_current_chat()
            st.session_state.messages = []
            st.session_state.uploaded_files_data = []
            st.session_state.active_agents = set()
            st.session_state.completed_agents = set()
            st.session_state.processing = False
            st.session_state.pending_input = None
            st.session_state.current_session_id = None
            st.rerun()

        options = ["auto"] + list(registered_agents)
        labels = {
            "auto": "Auto — Manager decides",
        }
        for name in registered_agents:
            labels[name] = agent_label(name)

        current = st.session_state.get("preferred_agent", "auto")
        if current not in options:
            current = "auto"

        selected = st.selectbox(
            "Preferred specialist",
            options=options,
            index=options.index(current),
            format_func=lambda value: labels.get(value, value),
            help="Optional hint only. The Manager still builds the real execution plan.",
        )
        st.session_state.preferred_agent = selected

        st.markdown('<div class="nav-label">Conversations</div>', unsafe_allow_html=True)
        history = st.session_state.get("chat_sessions", [])
        if history:
            for session in reversed(history[-8:]):
                preview = session.get("preview", "Untitled")
                if len(preview) > 34:
                    preview = preview[:34] + "…"
                session_id = session.get("id")
                if st.button(
                    preview,
                    key=f"hist_{session_id}",
                    use_container_width=True,
                ):
                    _archive_current_chat()
                    st.session_state.messages = [msg.copy() for msg in session.get("messages", [])]
                    st.session_state.current_session_id = session_id
                    st.session_state.uploaded_files_data = []
                    st.rerun()
        else:
            st.caption("No saved conversations yet.")

        from ui.file_upload import render_file_upload

        render_file_upload()

        st.markdown('<div class="nav-label">Agents</div>', unsafe_allow_html=True)
        active = st.session_state.get("active_agents", set())
        completed = st.session_state.get("completed_agents", set())

        for name in registered_agents:
            is_live = name in active
            is_done = name in completed and not is_live
            state_class = "active" if is_live or is_done else ""
            dot_class = "on" if is_live or is_done else ""
            suffix = " · running" if is_live else (" · used" if is_done else "")
            st.markdown(
                f"""
                <div class="agent-row {state_class}">
                    <span class="agent-dot {dot_class}"></span>
                    <div>
                        <div class="agent-name">{agent_icon(name)} {agent_label(name)}{suffix}</div>
                        <div class="agent-role">{agent_role(name)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="padding: 14px 8px 4px 8px; margin-top: 10px; border-top: 1px solid var(--border);">
                <div style="font-size: 12px; font-weight: 650; color: var(--text);">System</div>
                <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 3px; line-height: 1.4;">
                    Orchestrator coordinates registered agents. Provider keys stay in your existing environment configuration.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _archive_current_chat() -> None:
    """Store the open conversation in sidebar history if it has messages."""
    messages = st.session_state.get("messages", [])
    if not messages:
        return

    preview = "Untitled conversation"
    for msg in messages:
        if msg.get("role") == "user" and str(msg.get("content", "")).strip():
            preview = str(msg["content"]).strip()
            break

    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []

    current_id = st.session_state.get("current_session_id")
    payload = {
        "id": current_id or f"chat_{len(st.session_state.chat_sessions) + 1}_{len(messages)}",
        "preview": preview,
        "messages": [msg.copy() for msg in messages],
    }

    if current_id:
        for index, session in enumerate(st.session_state.chat_sessions):
            if session.get("id") == current_id:
                st.session_state.chat_sessions[index] = payload
                return

    st.session_state.chat_sessions.append(payload)
    st.session_state.current_session_id = payload["id"]
