import re

from agents.base_agent import BaseAgent


class CommunicationAgent(BaseAgent):
    """
    Communication Agent for CHORUS.

    Prepares emails/messages but never sends them during generation.
    Email requests are returned as a structured approval_required action.
    Actual sending happens only through route_email(), after explicit
    user approval.
    """

    def __init__(self, provider: str = "gemini"):
        super().__init__("communication", provider)

    # =========================================================
    # MAIN ENTRY POINT
    # =========================================================

    def run(self, task: str):
        task = str(task).strip()

        if not task:
            return {
                "type": "error",
                "message": "Communication task cannot be empty.",
            }

        if self._is_email_request(task):
            return self._prepare_email(task)

        prompt = f"""
You are CHORUS's Communication Agent.

Complete ONLY this communication task:

{task}

Rules:
- Do not send anything.
- Do not claim anything was sent.
- Preserve the user's information.
- Do not invent missing facts.
- Do not perform research, coding, or data analysis.
- Return only the requested communication.
"""

        try:
            response = self.invoke(prompt)
            return self._normalize_response(response.content)

        except Exception as error:
            return {
                "type": "error",
                "message": "Communication generation failed.",
                "error": str(error),
            }

    # =========================================================
    # EMAIL PREPARATION
    # =========================================================

    def _prepare_email(self, task: str) -> dict:
        """
        Prepare an email and return an approval action.

        The email is NEVER sent here.
        """

        prompt = f"""
You are CHORUS's Communication Agent.

Prepare the email described below.

USER REQUEST:

{task}

Rules:

1. NEVER send the email.
2. Preserve the recipient exactly.
3. Preserve the requested subject exactly.
4. Preserve the requested message exactly when supplied.
5. If no message is supplied, write a concise professional body.
6. Use Gmail unless another supported platform is explicitly requested.
7. Never invent a recipient.
8. If an email address is present in the user's request, copy it exactly.
9. Return ONLY this format:

OPERATION: CREATE_EMAIL
PLATFORM: gmail
TO: <recipient or Not provided>
CC: <None or recipients>
BCC: <None or recipients>
SUBJECT: <subject>
MESSAGE: <email body>
ATTACHMENTS: <None or comma-separated attachments>
SEND_STATUS: READY_FOR_AUTHORIZED_TOOL
"""

        try:
            response = self.invoke(prompt)
            raw = self._normalize_response(response.content)

        except Exception as error:
            return {
                "type": "error",
                "message": "Email preparation failed.",
                "error": str(error),
            }

        # First try the structured LLM response.
        parsed = self._parse_email_operation(raw)

        # If structured parsing fails, extract information directly
        # from the user's request.
        if parsed is None:
            parsed = self._extract_email_from_task(task, raw)

        if parsed is None:
            return {
                "type": "error",
                "message": (
                    "Communication Agent could not prepare a valid email action."
                ),
                "raw_response": raw,
            }

        parsed["status"] = "approval_required"
        parsed["action"] = "send_email"
        parsed["sent"] = False

        return parsed

    @staticmethod
    def _is_email_request(task: str) -> bool:
        text = task.lower()

        return any(
            term in text
            for term in (
                "email",
                "e-mail",
                "gmail",
                "send an email",
                "send email",
                "draft an email",
                "draft email",
                "create an email",
                "create email",
                "prepare an email",
                "prepare email",
            )
        )

    # =========================================================
    # STRUCTURED EMAIL PARSING
    # =========================================================

    @classmethod
    def _parse_email_operation(cls, text: str):
        """
        Parse the structured response returned by the LLM.

        Supports both:

            TO: user@example.com

        and:

            *TO*: user@example.com
        """

        text = str(text).strip()
        upper = text.upper()

        if "CREATE_EMAIL" not in upper and "REPLY_EMAIL" not in upper:
            return None

        operation = cls._extract_field(text, "OPERATION")
        platform = cls._extract_field(text, "PLATFORM") or "gmail"

        to = cls._extract_field(text, "TO") or ""
        cc = cls._extract_field(text, "CC")
        bcc = cls._extract_field(text, "BCC")

        subject = cls._extract_field(text, "SUBJECT") or ""
        message = cls._extract_field(text, "MESSAGE") or ""

        attachments = cls._extract_field(text, "ATTACHMENTS")

        if not operation:
            return None

        operation = cls._clean_field_value(operation).upper()

        if operation not in {"CREATE_EMAIL", "REPLY_EMAIL"}:
            return None

        platform = cls._clean_field_value(platform).lower()

        if platform in {
            "",
            "unspecified",
            "not provided",
            "none",
        }:
            platform = "gmail"

        to = cls._clean_required(to)
        subject = cls._clean_required(subject)
        message = cls._clean_required(message)

        # -----------------------------------------------------
        # IMPORTANT:
        # Do not allow "Not provided" to become a recipient.
        # -----------------------------------------------------

        if not to or not cls._contains_email_address(to):
            return None

        if not subject or not message:
            return None

        attachment_list = []

        if attachments:
            cleaned_attachments = cls._clean_field_value(attachments)

            if cleaned_attachments.lower() not in {
                "none",
                "not provided",
                "n/a",
                "",
            }:
                attachment_list = [
                    item.strip()
                    for item in cleaned_attachments.split(",")
                    if item.strip()
                ]

        return {
            "status": "approval_required",
            "action": "send_email",
            "platform": platform,
            "to": to,
            "cc": cls._normalize_optional(cc),
            "bcc": cls._normalize_optional(bcc),
            "subject": subject,
            "message": message,
            "attachments": attachment_list,
            "sent": False,
        }

    # =========================================================
    # FALLBACK EMAIL EXTRACTION
    # =========================================================

    @classmethod
    def _extract_email_from_task(cls, task: str, generated: str):
        """
        Fallback for LLM responses that fail to follow the
        structured email format.

        The recipient is extracted directly from the user's
        request so the LLM cannot accidentally replace it with
        "Not provided" or another value.
        """

        task = str(task).strip()
        generated = str(generated).strip()

        # -----------------------------------------------------
        # RECIPIENT
        # -----------------------------------------------------

        email_match = re.search(
            r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
            task,
            flags=re.IGNORECASE,
        )

        to = email_match.group(0).strip() if email_match else ""

        # -----------------------------------------------------
        # SUBJECT
        # -----------------------------------------------------

        subject = ""

        subject_patterns = [
            r'\bsubject\s*(?:is|:)?\s*["\']([^"\']+)["\']',
            r"\bsubject\s*(?:is|:)?\s*(.+?)(?=\s+\bmessage\b|\s*$)",
        ]

        for pattern in subject_patterns:
            match = re.search(
                pattern,
                task,
                flags=re.IGNORECASE | re.DOTALL,
            )

            if match:
                subject = match.group(1).strip()
                break

        # -----------------------------------------------------
        # MESSAGE
        # -----------------------------------------------------

        message = ""

        message_patterns = [
            r'\bmessage\s*(?:is|:)?\s*["\'](.+?)["\']\s*$',
            r"\bmessage\s*(?:is|:)?\s*(.+?)\s*$",
        ]

        for pattern in message_patterns:
            match = re.search(
                pattern,
                task,
                flags=re.IGNORECASE | re.DOTALL,
            )

            if match:
                message = match.group(1).strip()
                break

        # If the user did not explicitly provide a message,
        # use the generated body from the LLM.
        if not message:
            message = cls._clean_generated_content(generated)

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        if not to:
            return None

        if not cls._contains_email_address(to):
            return None

        if not subject:
            return None

        if not message:
            return None

        return {
            "status": "approval_required",
            "action": "send_email",
            "platform": "gmail",
            "to": to,
            "cc": None,
            "bcc": None,
            "subject": subject,
            "message": message,
            "attachments": [],
            "sent": False,
        }

    # =========================================================
    # FIELD EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_field(text: str, field_name: str):
        """
        Extract a field from structured LLM output.

        Supported:

            TO: user@example.com

        and:

            *TO*: user@example.com
        """

        fields = (
            "OPERATION",
            "PLATFORM",
            "TO",
            "CC",
            "BCC",
            "SUBJECT",
            "MESSAGE",
            "ATTACHMENTS",
            "SEND_STATUS",
        )

        field_pattern = (
            rf"^\s*(?:\*{re.escape(field_name)}\*"
            rf"|{re.escape(field_name)})\s*:\s*(.*?)"
        )

        next_fields = "|".join(
            re.escape(field)
            for field in fields
            if field != field_name
        )

        pattern = re.compile(
            rf"(?ims){field_pattern}"
            rf"(?=^\s*(?:\*?(?:{next_fields})\*?)\s*:|\Z)"
        )

        match = pattern.search(str(text))

        if not match:
            return None

        return match.group(1).strip()

    # =========================================================
    # CLEANING / NORMALIZATION
    # =========================================================

    @staticmethod
    def _clean_field_value(value: str) -> str:
        """
        Remove harmless markdown/code formatting around
        structured field values.
        """

        value = str(value).strip()

        value = value.replace("```text", "")
        value = value.replace("```", "")
        value = value.strip()

        if value.startswith("*") and value.endswith("*"):
            value = value[1:-1].strip()

        return value

    @staticmethod
    def _clean_required(value: str) -> str:
        value = CommunicationAgent._clean_field_value(value)

        if value.lower() in {
            "none",
            "not provided",
            "n/a",
            "null",
            "unknown",
        }:
            return ""

        return value

    @staticmethod
    def _normalize_optional(value):
        if value is None:
            return None

        value = CommunicationAgent._clean_field_value(value)

        if value.lower() in {
            "",
            "none",
            "not provided",
            "n/a",
            "null",
            "unknown",
        }:
            return None

        return value

    @staticmethod
    def _contains_email_address(value: str) -> bool:
        """
        Validate that a recipient contains at least one
        syntactically recognizable email address.
        """

        return bool(
            re.search(
                r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
                str(value),
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _clean_generated_content(content: str) -> str:
        """
        Extract MESSAGE from a structured generated response
        if available.
        """

        text = str(content).strip()

        match = re.search(
            r"(?ims)^\s*(?:\*MESSAGE\*|MESSAGE)\s*:\s*(.*?)"
            r"(?=^\s*(?:\*?(?:ATTACHMENTS|SEND_STATUS)\*?)\s*:|\Z)",
            text,
        )

        if match:
            return match.group(1).strip()

        return (
            text
            .replace("```text", "")
            .replace("```", "")
            .strip()
        )

    @staticmethod
    def _normalize_response(content) -> str:
        """
        Normalize LangChain/Gemini response content.
        """

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict) and item.get("text"):
                    parts.append(str(item["text"]))

                elif isinstance(item, str):
                    parts.append(item)

            return "\n".join(parts).strip()

        return str(content).strip()

    # =========================================================
    # APPROVED EMAIL SENDING
    # =========================================================

    def route_email(
        self,
        platform: str,
        to: str,
        subject: str,
        message: str,
        cc: str | None = None,
        bcc: str | None = None,
        attachments: list[str] | None = None,
    ) -> dict:
        """
        Send an email only after the Orchestrator receives
        explicit user approval.
        """

        # Safety validation before the actual communication tool.
        if not to or not self._contains_email_address(to):
            return {
                "type": "error",
                "message": "Missing or invalid email recipient.",
                "sent": False,
            }

        if not subject:
            return {
                "type": "error",
                "message": "Missing email subject.",
                "sent": False,
            }

        if not message:
            return {
                "type": "error",
                "message": "Missing email message.",
                "sent": False,
            }

        from communication_tools.router import CommunicationRouter

        router = CommunicationRouter()

        return router.send_email(
            platform=platform,
            to=to,
            subject=subject,
            message=message,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )