"""
Live workflow status.

Intercepts print() output from the existing orchestrator and Manager
messages so the dashboard can show real processing stages:

Request received → Manager analyzing → Agents selected → Task execution → Response

No backend modules are modified. Updates from worker threads are applied
after those threads finish, because Streamlit UI calls must stay on the
script thread when possible.
"""

import io
import re
import sys
import threading

import streamlit as st

from main import MultiAgentWorkflow
from ui.agents import agent_label

PIPELINE_STEPS = [
    ("received", "Request received"),
    ("processing", "Processing"),
    ("agents", "Agent selected"),
    ("execution", "Task execution"),
    ("response", "Response"),
]


class OutputInterceptor(io.TextIOBase):
    """Capture orchestrator prints and translate them into UI updates."""

    def __init__(self, original_stdout, on_update=None):
        super().__init__()
        self.original = original_stdout
        self.on_update = on_update
        self.updates = []
        self.seen_assigned = False
        self.lock = threading.Lock()

    def write(self, text):
        if self.original:
            self.original.write(text)

        if not text or not text.strip():
            return len(text) if text else 0

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            with self.lock:
                update = self._parse_line(line)
                if update:
                    self.updates.append(update)
                    self._emit(update)

        return len(text)

    def flush(self):
        if self.original:
            self.original.flush()

    def _emit(self, update: dict) -> None:
        if not self.on_update:
            return
        if threading.current_thread() is not threading.main_thread():
            return
        self.on_update(update)

    def _parse_line(self, line: str) -> dict | None:
        if line == "USER REQUEST":
            return {
                "stage": "received",
                "icon": "1",
                "text": "Request received",
            }

        if "[MANAGER] ANALYZING REQUEST" in line:
            return {
                "stage": "processing",
                "icon": "2",
                "text": "Manager analyzing the request and assigning agents",
                "agent": "manager",
            }

        if "[MANAGER] EXECUTION PLAN CREATED" in line:
            return {
                "stage": "agents",
                "icon": "3",
                "text": "Execution plan created — specialists selected",
                "agent": "manager",
            }

        if line == "ASSIGNED TASKS":
            self.seen_assigned = True
            return {
                "stage": "agents",
                "icon": "3",
                "text": "Assigned tasks",
            }

        if self.seen_assigned and "→" in line and not line.startswith("[") and not line.startswith("Depends"):
            parts = [part.strip() for part in line.split("→")]
            if len(parts) >= 3:
                agent_name = parts[1]
                task_desc = parts[2]
                return {
                    "stage": "agents",
                    "icon": "3",
                    "text": f"{agent_label(agent_name)} selected — {task_desc}",
                    "agent": agent_name.lower(),
                }

        if line.startswith("[RUNNING]"):
            agent_info = line.replace("[RUNNING]", "").strip()
            agent_name = agent_info
            task_desc = ""
            if "→" in agent_info:
                left, right = agent_info.split("→", 1)
                agent_name = left.strip()
                task_desc = right.strip()
            agent_name = agent_name.lower().replace(" ", "_")
            label = agent_label(agent_name)
            detail = f": {task_desc}" if task_desc else ""
            return {
                "stage": "execution",
                "icon": "4",
                "text": f"Running {label}{detail}",
                "agent": agent_name.lower().replace(" ", "_"),
            }

        if line.startswith("[COMPLETED]"):
            agent_name = line.replace("[COMPLETED]", "").strip().lower().replace(" ", "_")
            return {
                "stage": "execution",
                "icon": "4",
                "text": f"{agent_label(agent_name)} completed",
                "agent": agent_name,
                "completed": True,
            }

        if "DEVELOPMENT LOOP" in line:
            match = re.search(r"ATTEMPT (\d+)/(\d+)", line)
            if match:
                return {
                    "stage": "execution",
                    "icon": "4",
                    "text": f"Development loop attempt {match.group(1)} of {match.group(2)}",
                }

        if "[DEVELOPMENT] TESTS PASSED" in line:
            return {
                "stage": "execution",
                "icon": "4",
                "text": "Tests passed",
            }

        if "[DEVELOPMENT] TESTS FAILED" in line:
            return {
                "stage": "execution",
                "icon": "4",
                "text": "Tests failed — debugger and code fixer engaged",
            }

        if "[MANAGER] CREATING FINAL RESPONSE" in line:
            return {
                "stage": "response",
                "icon": "5",
                "text": "Manager composing the final response",
                "agent": "manager",
            }

        return None

    def get_updates(self) -> list:
        with self.lock:
            return self.updates.copy()


def _pipeline_html(current_stage: str) -> str:
    order = [step[0] for step in PIPELINE_STEPS]
    current_index = order.index(current_stage) if current_stage in order else 0
    chips = []
    for index, (key, label) in enumerate(PIPELINE_STEPS):
        css = "current" if index == current_index else ("done" if index < current_index else "")
        chips.append(f'<span class="pipeline-step {css}">{index + 1}. {label}</span>')
    return f'<div class="pipeline">{"".join(chips)}</div>'


def run_workflow_with_status(workflow: MultiAgentWorkflow, request: str) -> dict | None:
    """Run MultiAgentWorkflow.run() while rendering real orchestrator progress."""
    interceptor = OutputInterceptor(sys.stdout)
    original_stdout = sys.stdout
    result = None
    error = None
    current_stage = "received"
    emitted = 0

    stepper = st.empty()
    stepper.markdown(_pipeline_html(current_stage), unsafe_allow_html=True)

    def on_update(update: dict) -> None:
        nonlocal current_stage, emitted
        stage = update.get("stage")
        if stage:
            current_stage = stage
            stepper.markdown(_pipeline_html(current_stage), unsafe_allow_html=True)

        agent = update.get("agent")
        if agent:
            active = set(st.session_state.get("active_agents", set()))
            completed = set(st.session_state.get("completed_agents", set()))
            if update.get("completed"):
                active.discard(agent)
                completed.add(agent)
            else:
                active.add(agent)
            st.session_state.active_agents = active
            st.session_state.completed_agents = completed

        st.write(f"{update.get('icon', '•')} {update.get('text', '')}")
        emitted += 1

    interceptor.on_update = on_update

    with st.status("Processing with the multi-agent workflow…", expanded=True) as status:
        try:
            st.write("1 Request received")
            sys.stdout = interceptor
            st.session_state.active_agents = set()
            result = workflow.run(request)
            sys.stdout = original_stdout

            remaining = interceptor.get_updates()[emitted:]
            for update in remaining:
                on_update(update)

            current_stage = "response"
            stepper.markdown(_pipeline_html(current_stage), unsafe_allow_html=True)
            status.update(
                label="All assigned tasks completed",
                state="complete",
                expanded=False,
            )
        except Exception as exc:
            sys.stdout = original_stdout
            error = exc
            remaining = interceptor.get_updates()[emitted:]
            for update in remaining:
                on_update(update)
            status.update(
                label="The workflow stopped with an error",
                state="error",
                expanded=True,
            )
        finally:
            sys.stdout = original_stdout
            st.session_state.active_agents = set()

    if error:
        _render_error(error)
        st.session_state.last_pipeline = interceptor.get_updates()
        return None

    if result is not None:
        result = dict(result)
        result["pipeline"] = interceptor.get_updates()

    st.session_state.last_pipeline = interceptor.get_updates()
    return result


def _render_error(error: Exception) -> None:
    error_text = str(error)
    lowered = error_text.lower()

    if "api" in lowered or "key" in lowered:
        friendly = "There is a problem reaching the language-model provider. Check the API keys already configured in your environment."
    elif "rate limit" in lowered:
        friendly = "The provider rate limit was reached. Wait a moment and send the request again."
    elif "did not assign any tasks" in lowered:
        friendly = "The Manager did not assign any tasks for this request. Try a more specific instruction."
    elif "is not registered" in lowered:
        friendly = "The plan referenced an agent that is not registered in this workspace."
    else:
        friendly = "An error occurred while the agents were working on this request."

    st.markdown(
        f"""
        <div class="error-card">
            <h4>Could not complete the task</h4>
            <p>{friendly}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Technical details", expanded=False):
        st.code(error_text, language="text")
