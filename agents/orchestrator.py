from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from agents.registry import AgentRegistry


class AgentOrchestrator:
    """
    Coordinates CHORUS agents.

    Responsibilities:
    - Route simple requests directly to specialized agents.
    - Delegate complex requests through the Manager Agent.
    - Execute independent tasks in parallel.
    - Pass conversation history to the Manager.
    - Pass uploaded-file metadata/path to relevant agents.
    - Handle software testing/fixing/review workflows.
    - Prepare communication actions for user approval.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    # ============================================================
    # BASIC HELPERS
    # ============================================================

    @staticmethod
    def _build_attachment_context(attachments=None):
        """
        Convert uploaded attachment metadata into a text context
        that can be passed to agents.

        Expected attachment format:

        {
            "id": "...",
            "filename": "sales_data.csv",
            "original_name": "sales_data.csv",
            "content_type": "text/csv",
            "size": 1234,
            "file_path": "C:/.../uploads/..."
        }
        """

        if not attachments:
            return ""

        lines = [
            "ATTACHED FILES:",
            "The user uploaded the following file(s).",
            "Use the FILE_PATH when you need to read or analyze the actual file.",
            "",
        ]

        for index, attachment in enumerate(attachments, start=1):
            if not isinstance(attachment, dict):
                continue

            filename = (
                attachment.get("original_name")
                or attachment.get("filename")
                or "unknown_file"
            )

            content_type = (
                attachment.get("content_type")
                or attachment.get("mime_type")
                or "unknown"
            )

            file_path = (
                attachment.get("file_path")
                or attachment.get("path")
                or attachment.get("stored_path")
                or ""
            )

            size = attachment.get("size")

            lines.append(f"FILE {index}: {filename}")
            lines.append(f"TYPE: {content_type}")

            if size is not None:
                lines.append(f"SIZE: {size} bytes")

            if file_path:
                lines.append(f"FILE_PATH: {file_path}")

            lines.append("")

        return "\n".join(lines).strip()

    @staticmethod
    def _append_attachment_context(task, attachments=None):
        """
        Append attachment information to an agent task.
        """

        if not attachments:
            return task

        attachment_context = AgentOrchestrator._build_attachment_context(
            attachments
        )

        if not attachment_context:
            return task

        return f"{task}\n\n{attachment_context}"

    @staticmethod
    def _normalize_attachments(attachments):
        """
        Ensure attachments are always represented as a list.
        """

        if not attachments:
            return []

        if isinstance(attachments, dict):
            return [attachments]

        if isinstance(attachments, list):
            return attachments

        return []

    # ============================================================
    # SIMPLE AGENT ROUTING
    # ============================================================

    def _detect_simple_agent(self, request: str):
        """
        Detect requests that can be handled directly by a single
        specialized agent.

        Priority matters here.
        """

        if not request:
            return None

        text = request.lower()

        # Communication
        communication_keywords = [
            "send email",
            "send an email",
            "email",
            "mail",
            "gmail",
            "send a message",
            "send message",
        ]

        if any(keyword in text for keyword in communication_keywords):
            return "communication"

        # Document
        document_keywords = [
            "create document",
            "create a document",
            "make a document",
            "generate document",
            "generate a document",
            "write a document",
            "create pdf",
            "generate pdf",
            "create report",
            "generate report",
            "document",
            "pdf",
            "report",
        ]

        if any(keyword in text for keyword in document_keywords):
            return "document"

        # Data analysis
        data_keywords = [
            "analyze data",
            "analyse data",
            "analyze this data",
            "analyse this data",
            "analyze the data",
            "analyse the data",
            "csv",
            "excel",
            "spreadsheet",
            "xlsx",
            "xls",
            "sales data",
            "data analysis",
            "statistics",
            "calculate total",
            "calculate average",
            "find the average",
            "find total",
            "analyze",
            "analyse",
        ]

        if any(keyword in text for keyword in data_keywords):
            return "data"

        # Research
        research_keywords = [
            "research",
            "search the web",
            "search online",
            "look up",
            "find information",
            "latest information",
            "latest news",
            "what is",
            "who is",
            "compare",
        ]

        if any(keyword in text for keyword in research_keywords):
            return "research"

        # Content
        content_keywords = [
            "write",
            "rewrite",
            "summarize",
            "summarise",
            "blog",
            "article",
            "caption",
            "social media",
            "creative",
        ]

        if any(keyword in text for keyword in content_keywords):
            return "content"

        # Developer
        developer_keywords = [
            "code",
            "coding",
            "program",
            "programming",
            "function",
            "python",
            "javascript",
            "react",
            "api",
            "debug",
            "fix this code",
            "implement",
            "build",
        ]

        if any(keyword in text for keyword in developer_keywords):
            return "developer"

        return None

    def _run_simple_request(
        self,
        request: str,
        agent_name: str,
        attachments=None,
    ):
        """
        Run a request directly through one specialized agent.
        """

        agent = self.registry.get(agent_name)

        if agent is None:
            raise ValueError(
                f"Agent '{agent_name}' is not registered."
            )

        agent_request = self._append_attachment_context(
            request,
            attachments,
        )

        # Communication is special because it requires approval
        # before the actual email is sent.
        if agent_name == "communication":
            return self._prepare_communication(agent, agent_request)

        return agent.run(agent_request)

    # ============================================================
    # COMMUNICATION
    # ============================================================

    def _extract_email_action(self, result):
        """
        Extract a communication action from an agent result.

        The Communication Agent may return either a dictionary
        or a normal text response.
        """

        if not isinstance(result, dict):
            return None

        return (
            result.get("email_action")
            or result.get("communication_action")
            or result.get("action")
        )

    def _prepare_communication(self, agent, request):
        """
        Prepare an email/message action for user approval.
        """

        result = agent.run(request)

        if isinstance(result, dict):
            email_action = (
                result.get("email_action")
                or result.get("communication_action")
            )

            if email_action:
                return {
                    "results": [result],
                    "final_response": result.get(
                        "response",
                        "I prepared the communication for your review.",
                    ),
                    "email_action": email_action,
                }

        return {
            "results": [result],
            "final_response": (
                result
                if isinstance(result, str)
                else "I prepared the communication for your review."
            ),
            "email_action": self._extract_email_action(result),
        }

    def send_approved_email(
        self,
        to: str,
        subject: str,
        message: str,
    ):
        """
        Send an approved email through the Communication Agent.
        """

        agent = self.registry.get("communication")

        if agent is None:
            raise ValueError(
                "Communication Agent is not registered."
            )

        if hasattr(agent, "send_email"):
            return agent.send_email(
                to=to,
                subject=subject,
                message=message,
            )

        if hasattr(agent, "send_approved_email"):
            return agent.send_approved_email(
                to=to,
                subject=subject,
                message=message,
            )

        raise AttributeError(
            "Communication Agent does not provide an email sending method."
        )

    # ============================================================
    # TASK EXECUTION
    # ============================================================

    def _execute_task(
        self,
        task,
        previous_results=None,
        attachments=None,
    ):
        """
        Execute one Manager-generated task.

        Dependency results are included in the task context.
        Uploaded files are also included so agents can access them.
        """

        previous_results = previous_results or {}

        task_description = ""

        if isinstance(task, dict):
            task_description = (
                task.get("description")
                or task.get("task")
                or task.get("request")
                or task.get("instruction")
                or ""
            )
        else:
            task_description = str(task)

        if not task_description:
            raise ValueError("Task description is empty.")

        # --------------------------------------------------------
        # Add dependency results
        # --------------------------------------------------------

        dependency_results = []

        if isinstance(task, dict):
            dependencies = (
                task.get("dependencies")
                or task.get("depends_on")
                or []
            )

            for dependency in dependencies:
                if dependency in previous_results:
                    dependency_results.append(
                        f"RESULT FROM {dependency}:\n"
                        f"{previous_results[dependency]}"
                    )

        if dependency_results:
            task_description += (
                "\n\n"
                "PREVIOUS TASK RESULTS:\n"
                + "\n\n".join(dependency_results)
            )

        # --------------------------------------------------------
        # Add uploaded-file context
        # --------------------------------------------------------

        task_description = self._append_attachment_context(
            task_description,
            attachments,
        )

        # --------------------------------------------------------
        # Resolve agent
        # --------------------------------------------------------

        agent_name = None

        if isinstance(task, dict):
            agent_name = (
                task.get("agent")
                or task.get("agent_name")
                or task.get("assigned_agent")
            )

        if not agent_name:
            agent_name = self._detect_simple_agent(
                task_description
            )

        if not agent_name:
            raise ValueError(
                "Unable to determine an agent for the task."
            )

        agent = self.registry.get(agent_name)

        if agent is None:
            raise ValueError(
                f"Agent '{agent_name}' is not registered."
            )

        # --------------------------------------------------------
        # Execute
        # --------------------------------------------------------

        if agent_name == "communication":
            return self._prepare_communication(
                agent,
                task_description,
            )

        return agent.run(task_description)

    # ============================================================
    # SOFTWARE WORKFLOW
    # ============================================================

    def _run_software_test_fix_loop(
        self,
        request,
        results,
    ):
        """
        Run the software testing/fixing workflow when requested.
        """

        tester = self.registry.get("tester")
        debugger = self.registry.get("debugger")
        code_fixer = self.registry.get("code_fixer")

        if tester is None:
            return results

        test_result = tester.run(request)

        results["tester"] = test_result

        # If no debugger/fixer exists, simply return the test result.
        if debugger is None or code_fixer is None:
            return results

        # --------------------------------------------------------
        # Detect whether the test indicates a failure.
        # --------------------------------------------------------

        test_text = str(test_result).lower()

        failure_indicators = [
            "failed",
            "failure",
            "error",
            "exception",
            "broken",
            "not working",
            "test failed",
        ]

        has_failure = any(
            indicator in test_text
            for indicator in failure_indicators
        )

        if not has_failure:
            return results

        # --------------------------------------------------------
        # Debug
        # --------------------------------------------------------

        debug_result = debugger.run(
            f"""
Analyze the following test result and identify the root cause.

ORIGINAL REQUEST:
{request}

TEST RESULT:
{test_result}
""".strip()
        )

        results["debugger"] = debug_result

        # --------------------------------------------------------
        # Fix
        # --------------------------------------------------------

        fix_result = code_fixer.run(
            f"""
Fix the issue identified by the debugger.

ORIGINAL REQUEST:
{request}

TEST RESULT:
{test_result}

DEBUG RESULT:
{debug_result}
""".strip()
        )

        results["code_fixer"] = fix_result

        return results

    def _run_code_review(self, request, results):
        """
        Run Code Reviewer when the workflow indicates that code
        review is appropriate.
        """

        reviewer = self.registry.get("code_reviewer")

        if reviewer is None:
            return None

        review_request = f"""
Review the implementation/work produced for this request.

REQUEST:
{request}

RESULTS:
{results}
""".strip()

        return reviewer.run(review_request)

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    def _build_final_response(
        self,
        request,
        results,
    ):
        """
        Generate a final response from workflow results.

        Uses the Manager Agent when possible, otherwise returns
        a deterministic summary.
        """

        manager = self.registry.get("manager")

        if manager is not None:
            try:
                final_request = f"""
Provide the final response to the user.

USER REQUEST:
{request}

WORKFLOW RESULTS:
{results}

Give a clear, concise response.
Do not expose internal orchestration details unless useful.
""".strip()

                return manager.run(
                    request=final_request,
                    history=[],
                )
            except Exception:
                pass

        # --------------------------------------------------------
        # Deterministic fallback
        # --------------------------------------------------------

        if not results:
            return (
                "I couldn't complete the requested task."
            )

        if len(results) == 1:
            value = next(iter(results.values()))

            if isinstance(value, dict):
                return (
                    value.get("final_response")
                    or value.get("response")
                    or str(value)
                )

            return str(value)

        return (
            "I completed the requested workflow. "
            "The individual agent results were processed successfully."
        )

    # ============================================================
    # MAIN ORCHESTRATION
    # ============================================================

    def run(
        self,
        request: str,
        history=None,
        attachments=None,
        mode=None,
    ):
        """
        Main CHORUS orchestration entry point.

        Parameters:
            request:
                Current user request.

            history:
                Previous conversation messages.

            attachments:
                Uploaded file metadata from /api/upload.

            mode:
                Optional frontend mode. Currently retained for
                future routing/behavior customization.
        """

        if not request or not request.strip():
            raise ValueError(
                "Request cannot be empty."
            )

        request = request.strip()

        history = history or []

        attachments = self._normalize_attachments(
            attachments
        )

        # --------------------------------------------------------
        # SIMPLE REQUEST FAST PATH
        # --------------------------------------------------------

        simple_agent = self._detect_simple_agent(request)

        if simple_agent:
            result = self._run_simple_request(
                request=request,
                agent_name=simple_agent,
                attachments=attachments,
            )

            # Communication already returns structured data.
            if isinstance(result, dict):
                return result

            return {
                "results": {
                    simple_agent: result
                },
                "final_response": str(result),
                "email_action": None,
            }

        # --------------------------------------------------------
        # MANAGER WORKFLOW
        # --------------------------------------------------------

        manager = self.registry.get("manager")

        if manager is None:
            raise ValueError(
                "Manager Agent is not registered."
            )

        # Give Manager awareness of uploaded files so it can
        # correctly plan tasks involving those files.
        manager_request = request

        attachment_context = self._build_attachment_context(
            attachments
        )

        if attachment_context:
            manager_request = (
                f"{request}\n\n{attachment_context}"
            )

        # --------------------------------------------------------
        # Generate execution plan
        # --------------------------------------------------------

        execution_plan = manager.run(
            request=manager_request,
            history=history,
        )

        # --------------------------------------------------------
        # Normalize plan
        # --------------------------------------------------------

        if isinstance(execution_plan, dict):
            tasks = (
                execution_plan.get("tasks")
                or execution_plan.get("plan")
                or execution_plan.get("steps")
                or []
            )
        elif isinstance(execution_plan, list):
            tasks = execution_plan
        else:
            tasks = []

        # --------------------------------------------------------
        # If Manager didn't produce a usable plan, fallback
        # to direct routing.
        # --------------------------------------------------------

        if not tasks:
            fallback_agent = self._detect_simple_agent(
                request
            )

            if fallback_agent:
                result = self._run_simple_request(
                    request=request,
                    agent_name=fallback_agent,
                    attachments=attachments,
                )

                if isinstance(result, dict):
                    return result

                return {
                    "results": {
                        fallback_agent: result
                    },
                    "final_response": str(result),
                    "email_action": None,
                }

            return {
                "results": {},
                "final_response": (
                    "I couldn't determine the appropriate workflow "
                    "for that request."
                ),
                "email_action": None,
            }

        # --------------------------------------------------------
        # Execute tasks
        # --------------------------------------------------------

        results = {}

        pending_tasks = list(tasks)

        # We execute dependency-ready tasks in parallel.
        while pending_tasks:

            ready_tasks = []
            waiting_tasks = []

            completed_names = set(results.keys())

            for index, task in enumerate(pending_tasks):

                if not isinstance(task, dict):
                    ready_tasks.append(
                        (index, task)
                    )
                    continue

                dependencies = (
                    task.get("dependencies")
                    or task.get("depends_on")
                    or []
                )

                if all(
                    dependency in completed_names
                    for dependency in dependencies
                ):
                    ready_tasks.append(
                        (index, task)
                    )
                else:
                    waiting_tasks.append(
                        (index, task)
                    )

            # Prevent infinite loops caused by invalid dependencies.
            if not ready_tasks:
                for index, task in waiting_tasks:
                    task_name = (
                        task.get("id")
                        or task.get("name")
                        or f"task_{index + 1}"
                    )

                    results[task_name] = (
                        "Task could not be executed because "
                        "its dependencies were not completed."
                    )

                break

            next_pending = [
                task
                for index, task in waiting_tasks
            ]

            # ----------------------------------------------------
            # Parallel execution
            # ----------------------------------------------------

            with ThreadPoolExecutor(
                max_workers=min(
                    4,
                    max(1, len(ready_tasks)),
                )
            ) as executor:

                future_map = {}

                for index, task in ready_tasks:

                    task_name = (
                        task.get("id")
                        or task.get("name")
                        or f"task_{index + 1}"
                        if isinstance(task, dict)
                        else f"task_{index + 1}"
                    )

                    future = executor.submit(
                        self._execute_task,
                        task,
                        results.copy(),
                        attachments,
                    )

                    future_map[future] = task_name

                for future in as_completed(future_map):

                    task_name = future_map[future]

                    try:
                        task_result = future.result()

                        # Communication result may contain a nested
                        # structure. Preserve it as-is.
                        results[task_name] = task_result

                    except Exception as exc:
                        results[task_name] = {
                            "success": False,
                            "error": str(exc),
                        }

            pending_tasks = next_pending

        # --------------------------------------------------------
        # Software testing/fixing when appropriate
        # --------------------------------------------------------

        request_lower = request.lower()

        software_keywords = [
            "test",
            "testing",
            "debug",
            "fix",
            "bug",
            "error",
            "implementation",
            "code review",
            "review code",
        ]

        if any(
            keyword in request_lower
            for keyword in software_keywords
        ):
            try:
                results = self._run_software_test_fix_loop(
                    request,
                    results,
                )
            except Exception as exc:
                results["software_workflow"] = {
                    "success": False,
                    "error": str(exc),
                }

        # --------------------------------------------------------
        # Code review when explicitly requested
        # --------------------------------------------------------

        if (
            "code review" in request_lower
            or "review the code" in request_lower
            or "review this code" in request_lower
        ):
            try:
                review_result = self._run_code_review(
                    request,
                    results,
                )

                if review_result is not None:
                    results["code_reviewer"] = review_result

            except Exception as exc:
                results["code_reviewer"] = {
                    "success": False,
                    "error": str(exc),
                }

        # --------------------------------------------------------
        # Collect email action
        # --------------------------------------------------------

        email_action = None

        for value in results.values():

            if not isinstance(value, dict):
                continue

            candidate = (
                value.get("email_action")
                or value.get("communication_action")
            )

            if candidate:
                email_action = candidate
                break

            # Some agents may return the action inside a nested
            # result structure.
            nested_results = value.get("results")

            if isinstance(nested_results, list):

                for nested in nested_results:

                    if not isinstance(nested, dict):
                        continue

                    candidate = (
                        nested.get("email_action")
                        or nested.get("communication_action")
                    )

                    if candidate:
                        email_action = candidate
                        break

            if email_action:
                break

        # --------------------------------------------------------
        # Collect file/document action
        # --------------------------------------------------------

        file_action = None

        for value in results.values():

            if not isinstance(value, dict):
                continue

            candidate = (
                value.get("file_action")
                or value.get("document_action")
            )

            if candidate:
                file_action = candidate
                break

            nested_results = value.get("results")

            if isinstance(nested_results, list):

                for nested in nested_results:

                    if not isinstance(nested, dict):
                        continue

                    candidate = (
                        nested.get("file_action")
                        or nested.get("document_action")
                    )

                    if candidate:
                        file_action = candidate
                        break

            if file_action:
                break

        # --------------------------------------------------------
        # Final response
        # --------------------------------------------------------

        final_response = self._build_final_response(
            request,
            results,
        )

        # Manager/final-response agent can sometimes return a
        # structured dictionary. Normalize it for the API.
        if isinstance(final_response, dict):

            final_response_text = (
                final_response.get("final_response")
                or final_response.get("response")
                or final_response.get("message")
                or str(final_response)
            )

        else:
            final_response_text = str(
                final_response
            )

        return {
            "results": results,
            "final_response": final_response_text,
            "email_action": email_action,
            "file_action": file_action,
        }