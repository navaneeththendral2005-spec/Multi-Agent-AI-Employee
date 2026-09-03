from pathlib import Path
import re

from agents.base_agent import BaseAgent
from document_tools.reader import read_file
from document_tools.creator import create_document


class DocumentAgent(BaseAgent):
    """
    Document Agent for CHORUS.

    Responsibilities:
    - Read source documents when supplied.
    - Validate required source files before generation.
    - Refuse generation when a required file is missing.
    - Refuse generation when a supplied file does not contain
      the data required by the request.
    - Generate professional document content.
    - Create PDF, DOCX, PPTX, XLSX, and TXT files.
    - Return structured file metadata for the API.
    """

    def __init__(
        self,
        provider: str = "gemini"
    ):
        super().__init__(
            "document",
            provider
        )

    # =========================================================
    # DOCUMENT PROCESSING
    # =========================================================

    def run(
        self,
        task: str
    ) -> dict:
        """
        Execute a document-generation or document-processing task.

        Source-dependent requests are validated BEFORE the LLM is
        called. This prevents CHORUS from inventing missing data.
        """

        task = str(task).strip()

        if not task:
            return {
                "type": "error",
                "message": "Document task cannot be empty."
            }

        # -----------------------------------------------------
        # FIND INPUT FILE
        # -----------------------------------------------------

        file_path = self._find_file_path(task)

        # -----------------------------------------------------
        # DETERMINE WHETHER A SOURCE FILE IS REQUIRED
        # -----------------------------------------------------

        source_required = self._requires_source_file(task)

        # -----------------------------------------------------
        # REQUIRED FILE IS MISSING
        # -----------------------------------------------------

        if source_required and not file_path:

            return {
                "type": "error",
                "code": "SOURCE_FILE_REQUIRED",
                "message": (
                    "I can't generate this document yet because "
                    "the required source file is missing."
                ),
                "user_message": (
                    "I can't generate this document yet because "
                    "the required source file is missing. "
                    "Please upload the file containing the "
                    "requested data and try again."
                )
            }

        # -----------------------------------------------------
        # READ SOURCE FILE
        # -----------------------------------------------------

        extracted_content = ""

        if file_path:

            try:

                extracted_content = read_file(
                    file_path
                )

            except Exception as error:

                return {
                    "type": "error",
                    "code": "SOURCE_FILE_READ_FAILED",
                    "message": (
                        "The supplied source file could not "
                        "be read."
                    ),
                    "user_message": (
                        "I couldn't read the uploaded file. "
                        "Please check that the file is valid "
                        "and upload it again."
                    ),
                    "file": file_path,
                    "error": str(error)
                }

            extracted_content = str(
                extracted_content or ""
            ).strip()

        # -----------------------------------------------------
        # SOURCE FILE EXISTS BUT CONTAINS NO USABLE CONTENT
        # -----------------------------------------------------

        if source_required and not extracted_content:

            return {
                "type": "error",
                "code": "SOURCE_DATA_MISSING",
                "message": (
                    "The supplied source file does not contain "
                    "usable data."
                ),
                "user_message": (
                    "I can't generate this document because "
                    "the uploaded file does not contain usable "
                    "data for the requested document. "
                    "Please upload the correct file."
                ),
                "file": file_path
            }

        # -----------------------------------------------------
        # VALIDATE SOURCE CONTENT
        # -----------------------------------------------------

        if (
            source_required
            and file_path
        ):

            validation = self._validate_source_content(
                task,
                extracted_content
            )

            if not validation["valid"]:

                return {
                    "type": "error",
                    "code": "SOURCE_DATA_MISMATCH",
                    "message": validation["message"],
                    "user_message": validation["user_message"],
                    "file": file_path,
                    "missing_data": validation.get(
                        "missing_data",
                        []
                    )
                }

        # -----------------------------------------------------
        # PREPARE DOCUMENT CONTENT
        # -----------------------------------------------------

        if extracted_content:

            document_content = extracted_content

        else:

            document_content = (
                "No input document was provided. "
                "Generate the requested document directly "
                "from the assigned task."
            )

        # -----------------------------------------------------
        # LLM PROCESSING
        # -----------------------------------------------------

        prompt = f"""
You are CHORUS's Document Agent.

Complete ONLY the document task below.

ASSIGNED TASK:
{task}

SOURCE DOCUMENT CONTENT:
{document_content}

IMPORTANT DOCUMENT-GENERATION RULES:

1. Create the actual human-readable content for the
   requested document.

2. If source document content is supplied, preserve and
   accurately use the information from that source.

3. Do NOT invent data, statistics, names, figures, dates,
   financial values, or other facts that are not supported
   by the assigned task or source document.

4. Do NOT fabricate missing dataset values.

5. Do NOT provide Python code for creating the file.

6. Do NOT explain how to create the file.

7. Do NOT claim that binary document creation is impossible.

8. Return ONLY the actual human-readable document content
   that should be placed inside the requested file.

9. Use Markdown-style headings when useful:
   # Main Title
   ## Section
   ### Subsection

10. Use bullets when appropriate.

11. Preserve important facts from supplied source documents.

12. Keep the result professional, concise, and suitable for
    the requested document format.

13. Do not perform unrelated research, coding, or analysis.

RETURN ONLY DOCUMENT CONTENT.
"""

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return {
                "type": "error",
                "message": "Document generation failed.",
                "error": str(error)
            }

        # -----------------------------------------------------
        # NORMALIZE RESPONSE
        # -----------------------------------------------------

        content = self._normalize_content(
            response.content
        )

        if not content:

            return {
                "type": "error",
                "message": (
                    "Document Agent returned empty content."
                )
            }

        # -----------------------------------------------------
        # DETECT OUTPUT FORMAT
        # -----------------------------------------------------

        selected_format = (
            self._detect_output_format(
                task
            )
        )

        if selected_format is None:

            return {
                "type": "text",
                "content": content
            }

        # -----------------------------------------------------
        # CREATE FILENAME
        # -----------------------------------------------------

        filename = self._create_filename(
            task,
            selected_format
        )

        # -----------------------------------------------------
        # CREATE FILE
        # -----------------------------------------------------

        try:

            output_file = create_document(
                filename=filename,
                content=content,
                file_type=selected_format
            )

        except Exception as error:

            return {
                "type": "error",
                "message": "File creation failed.",
                "file_type": selected_format,
                "filename": filename,
                "error": str(error)
            }

        # -----------------------------------------------------
        # VERIFY FILE
        # -----------------------------------------------------

        output_path = Path(
            output_file
        )

        if not output_path.exists():

            return {
                "type": "error",
                "message": (
                    "The document creation process completed, "
                    "but the generated file could not be found."
                ),
                "file_type": selected_format,
                "filename": filename
            }

        # -----------------------------------------------------
        # STRUCTURED FILE RESULT
        # -----------------------------------------------------

        return {
            "type": "file",
            "content": content,
            "file": {
                "filename": output_path.name,
                "path": str(output_path),
                "file_type": selected_format,
                "size": output_path.stat().st_size
            }
        }

    # =========================================================
    # SOURCE FILE REQUIREMENT DETECTION
    # =========================================================

    @staticmethod
    def _requires_source_file(
        task: str
    ) -> bool:
        """
        Determine whether the user explicitly requires an
        existing file/dataset as the source for generation.

        Normal document requests such as:
            "Create a CHORUS overview PDF"

        are NOT source-dependent.

        Requests such as:
            "Create a sales report from this file"

        ARE source-dependent.
        """

        text = task.lower().strip()

        source_phrases = [
            # Explicit file references
            "from this file",
            "from the file",
            "from that file",
            "using this file",
            "using the file",
            "using that file",
            "based on this file",
            "based on the file",
            "based on that file",

            # Uploaded/attached files
            "from the uploaded file",
            "from an uploaded file",
            "using the uploaded file",
            "using an uploaded file",
            "based on the uploaded file",
            "based on an uploaded file",
            "from the attached file",
            "from an attached file",
            "using the attached file",
            "using an attached file",
            "based on the attached file",
            "based on an attached file",

            # Data source references
            "from this data",
            "from the data",
            "from that data",
            "using this data",
            "using the data",
            "using that data",
            "based on this data",
            "based on the data",
            "based on that data",

            # Dataset references
            "from this dataset",
            "from the dataset",
            "from that dataset",
            "using this dataset",
            "using the dataset",
            "using that dataset",
            "based on this dataset",
            "based on the dataset",
            "based on that dataset",

            # File-driven reports
            "analyze the uploaded",
            "analyse the uploaded",
            "analyze this csv",
            "analyse this csv",
            "analyze the csv",
            "analyse the csv",
            "analyze this excel",
            "analyse this excel",
            "analyze the excel",
            "analyse the excel",

            # Common source-driven document wording
            "generate a report from",
            "generate the report from",
            "create a report from",
            "create the report from",
            "make a report from",
            "prepare a report from",
            "generate a summary from",
            "create a summary from",
            "prepare a summary from",
            "create a document from",
            "generate a document from",
        ]

        return any(
            phrase in text
            for phrase in source_phrases
        )

    # =========================================================
    # SOURCE CONTENT VALIDATION
    # =========================================================

    @staticmethod
    def _validate_source_content(
        task: str,
        source_content: str
    ) -> dict:
        """
        Validate whether the supplied source contains the type
        of information requested by the task.

        This validation happens BEFORE the LLM generation call.

        It uses deterministic topic signals rather than another
        LLM call, helping conserve API quota.
        """

        task_lower = task.lower()
        content_lower = source_content.lower()

        # -----------------------------------------------------
        # NORMALIZE CONTENT FOR WORD MATCHING
        # -----------------------------------------------------

        normalized_content = re.sub(
            r"[^a-z0-9\s]",
            " ",
            content_lower
        )

        content_words = set(
            normalized_content.split()
        )

        # -----------------------------------------------------
        # DOMAIN SIGNALS
        # -----------------------------------------------------

        domain_groups = {
            "sales": {
                "sales",
                "sale",
                "revenue",
                "revenues",
                "customer",
                "customers",
                "orders",
                "order",
                "units",
                "quantity",
                "product",
                "products",
                "region",
                "regions",
                "salesperson",
                "salesperson",
            },

            "expense": {
                "expense",
                "expenses",
                "cost",
                "costs",
                "spending",
                "spend",
                "payment",
                "payments",
                "vendor",
                "vendors",
                "purchase",
                "purchases",
                "budget",
            },

            "finance": {
                "finance",
                "financial",
                "profit",
                "profits",
                "loss",
                "losses",
                "income",
                "revenue",
                "balance",
                "amount",
                "currency",
                "transaction",
                "transactions",
            },

            "employee": {
                "employee",
                "employees",
                "staff",
                "department",
                "departments",
                "salary",
                "salaries",
                "designation",
                "position",
                "manager",
                "joining",
                "hire",
                "hired",
            },

            "inventory": {
                "inventory",
                "stock",
                "stocks",
                "warehouse",
                "warehouses",
                "sku",
                "product",
                "products",
                "quantity",
                "available",
                "supplier",
                "suppliers",
            },

            "customer": {
                "customer",
                "customers",
                "client",
                "clients",
                "contact",
                "contacts",
                "phone",
                "email",
                "address",
                "account",
                "accounts",
            },

            "project": {
                "project",
                "projects",
                "milestone",
                "milestones",
                "task",
                "tasks",
                "deadline",
                "status",
                "owner",
                "deliverable",
                "deliverables",
            },
        }

        # -----------------------------------------------------
        # DETECT REQUESTED DOMAINS
        # -----------------------------------------------------

        requested_domains = []

        for domain, keywords in domain_groups.items():

            if any(
                keyword in task_lower
                for keyword in keywords
            ):

                requested_domains.append(
                    domain
                )

        # -----------------------------------------------------
        # DETECT SOURCE DOMAINS
        # -----------------------------------------------------

        source_domains = []

        for domain, keywords in domain_groups.items():

            matches = (
                keywords.intersection(
                    content_words
                )
            )

            if len(matches) >= 2:

                source_domains.append(
                    domain
                )

        # -----------------------------------------------------
        # SPECIFIC DOMAIN MISMATCH
        # -----------------------------------------------------

        if requested_domains:

            matched_domains = [
                domain
                for domain in requested_domains
                if domain in source_domains
            ]

            if not matched_domains:

                primary_domain = (
                    requested_domains[0]
                )

                readable_domain = (
                    primary_domain.replace(
                        "_",
                        " "
                    )
                )

                return {
                    "valid": False,
                    "message": (
                        "The supplied source file does not "
                        f"contain the requested {readable_domain} "
                        "data."
                    ),
                    "user_message": (
                        "I can't generate this document because "
                        "the uploaded file does not contain the "
                        f"requested {readable_domain} data. "
                        "Please upload the correct file."
                    ),
                    "missing_data": [
                        readable_domain
                    ]
                }

        # -----------------------------------------------------
        # EXPLICIT DATA ANALYSIS REQUEST
        # -----------------------------------------------------

        analysis_terms = [
            "analyze",
            "analyse",
            "analysis",
            "calculate",
            "compare",
            "comparison",
            "trend",
            "trends",
            "average",
            "percentage",
            "total",
            "statistics",
            "statistical",
            "growth",
        ]

        has_analysis_request = any(
            term in task_lower
            for term in analysis_terms
        )

        if has_analysis_request:

            # A source file should contain more than a tiny
            # amount of usable textual information.

            meaningful_words = [
                word
                for word in content_words
                if len(word) >= 3
            ]

            if len(meaningful_words) < 5:

                return {
                    "valid": False,
                    "message": (
                        "The supplied source file does not "
                        "contain enough data for the requested "
                        "analysis."
                    ),
                    "user_message": (
                        "I can't generate this document because "
                        "the uploaded file does not contain "
                        "enough data for the requested analysis. "
                        "Please upload a file containing the "
                        "required data."
                    ),
                    "missing_data": [
                        "usable source data"
                    ]
                }

        # -----------------------------------------------------
        # EXPLICIT REQUIRED DATA TERMS
        # -----------------------------------------------------

        # Remove generic instruction words and identify terms
        # that are likely to represent the actual requested data.

        generic_terms = {
            "create",
            "generate",
            "make",
            "prepare",
            "produce",
            "build",
            "export",
            "convert",
            "document",
            "report",
            "summary",
            "file",
            "pdf",
            "word",
            "excel",
            "spreadsheet",
            "powerpoint",
            "presentation",
            "from",
            "this",
            "that",
            "the",
            "using",
            "based",
            "uploaded",
            "attached",
            "data",
            "dataset",
            "please",
            "using",
            "with",
            "into",
            "as",
        }

        task_words = set(
            re.sub(
                r"[^a-z0-9\s]",
                " ",
                task_lower
            ).split()
        )

        meaningful_task_words = {
            word
            for word in task_words
            if len(word) >= 4
            and word not in generic_terms
        }

        # -----------------------------------------------------
        # CHECK IMPORTANT TASK TERMS AGAINST SOURCE
        # -----------------------------------------------------

        if meaningful_task_words:

            matched_terms = {
                word
                for word in meaningful_task_words
                if word in content_words
            }

            # Only enforce this when the request contains
            # several clearly meaningful terms. This prevents
            # normal source documents from being rejected merely
            # because wording differs slightly.

            if (
                len(meaningful_task_words) >= 3
                and len(matched_terms) == 0
                and not source_domains
            ):

                return {
                    "valid": False,
                    "message": (
                        "The supplied source file does not "
                        "appear to contain the data required "
                        "for the requested document."
                    ),
                    "user_message": (
                        "I can't generate this document because "
                        "the uploaded file does not appear to "
                        "contain the data required for the "
                        "request. Please upload the correct file."
                    ),
                    "missing_data": sorted(
                        meaningful_task_words
                    )[:5]
                }

        # -----------------------------------------------------
        # VALID
        # -----------------------------------------------------

        return {
            "valid": True,
            "message": "Source validation passed.",
            "user_message": "Source validation passed.",
            "missing_data": []
        }

    # =========================================================
    # CONTENT NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_content(
        content
    ) -> str:

        if isinstance(
            content,
            list
        ):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and item.get("text")
                ):

                    text_parts.append(
                        str(item["text"])
                    )

                elif isinstance(
                    item,
                    str
                ):

                    text_parts.append(
                        item
                    )

            return "\n".join(
                text_parts
            ).strip()

        return str(
            content
        ).strip()

    # =========================================================
    # INPUT FILE DETECTION
    # =========================================================

    @staticmethod
    def _find_file_path(
        task: str
    ):
        """
        Find an explicitly referenced existing source file.
        """

        extensions = (
            ".pdf",
            ".docx",
            ".pptx",
            ".csv",
            ".xlsx",
            ".xls",
            ".txt",
        )

        # -----------------------------------------------------
        # DIRECT PATH SEARCH
        # -----------------------------------------------------

        words = (
            task
            .replace('"', "")
            .replace("'", "")
            .split()
        )

        for word in words:

            cleaned_word = (
                word
                .strip()
                .rstrip(".,;:()[]{}")
            )

            path = Path(
                cleaned_word
            )

            if (
                path.suffix.lower()
                in extensions
                and path.exists()
            ):

                return str(
                    path
                )

        # -----------------------------------------------------
        # SEARCH FOR PATH-LIKE TOKENS INSIDE THE TASK
        # -----------------------------------------------------

        path_pattern = re.compile(
            r"""
            (?:
                [A-Za-z]:[\\/]
                |
                [./\\]
            )
            [^"'<>|]+?
            \.(?:pdf|docx|pptx|csv|xlsx|xls|txt)
            """,
            re.IGNORECASE | re.VERBOSE
        )

        matches = path_pattern.findall(
            task
        )

        for match in matches:

            cleaned = (
                match
                .strip()
                .rstrip(".,;:()[]{}")
            )

            path = Path(
                cleaned
            )

            if path.exists():

                return str(
                    path
                )

        return None

    # =========================================================
    # OUTPUT FORMAT DETECTION
    # =========================================================

    @staticmethod
    def _detect_output_format(
        task: str
    ):
        task_lower = task.lower()

        formats = [
            (
                (
                    "word document",
                    "microsoft word",
                    "docx",
                    ".docx",
                ),
                "docx",
            ),
            (
                (
                    "pdf",
                    ".pdf",
                ),
                "pdf",
            ),
            (
                (
                    "powerpoint",
                    "power point",
                    "pptx",
                    ".pptx",
                ),
                "pptx",
            ),
            (
                (
                    "excel",
                    "spreadsheet",
                    "xlsx",
                    ".xlsx",
                    "xls",
                    ".xls",
                ),
                "xlsx",
            ),
            (
                (
                    "text file",
                    "txt",
                    ".txt",
                ),
                "txt",
            ),
        ]

        for keywords, extension in formats:

            if any(
                keyword in task_lower
                for keyword in keywords
            ):

                return extension

        return None

    # =========================================================
    # FILENAME
    # =========================================================

    @staticmethod
    def _create_filename(
        task: str,
        extension: str
    ) -> str:

        task_lower = task.lower()

        if "chorus ai employee overview" in task_lower:
            base_name = "CHORUS_AI_Employee_Overview"

        elif "project overview" in task_lower:
            base_name = "CHORUS_Project_Overview"

        elif "project proposal" in task_lower:
            base_name = "CHORUS_Project_Proposal"

        elif "report" in task_lower:
            base_name = "CHORUS_Report"

        elif "summary" in task_lower:
            base_name = "CHORUS_Summary"

        else:
            base_name = "CHORUS_Document"

        return (
            f"{base_name}.{extension}"
        )