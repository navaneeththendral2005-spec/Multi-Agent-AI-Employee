import re
from pathlib import Path

from agents.base_agent import BaseAgent
from data_tools.analyzer import analyze_data


class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent for CHORUS.

    Supports:
    - CSV files
    - Excel files
    - Multiline CSV-style datasets
    - Inline natural-language datasets
    - Numerical summaries
    - Total and average calculations
    - Minimum and maximum values
    - Overall percentage growth
    - Month-to-month percentage changes
    - Pattern and trend analysis
    - Data quality checks
    - LLM-based interpretation
    """

    def __init__(
        self,
        provider: str = "gemini"
    ):
        super().__init__(
            "data_analyst",
            provider
        )

    # =========================================================
    # DATA ANALYSIS
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Execute the assigned data-analysis task.

        Supports:

        1. File-based datasets:
           CSV, XLSX, XLS

        2. Inline datasets:
           Data included directly inside the user's
           natural-language request.
        """

        # -----------------------------------------------------
        # FIND DATA FILE
        # -----------------------------------------------------

        file_path = self._find_data_file(
            task
        )

        analysis = None

        # -----------------------------------------------------
        # FILE-BASED ANALYSIS
        # -----------------------------------------------------

        if file_path:

            try:

                print(
                    "[DATA ANALYST] Analyzing file:",
                    file_path
                )

                analysis = analyze_data(
                    file_path
                )

            except Exception as error:

                return (
                    "Data analysis failed.\n"
                    f"File: {file_path}\n"
                    f"Error: {error}"
                )

        # -----------------------------------------------------
        # INLINE DATA ANALYSIS
        # -----------------------------------------------------

        else:

            inline_data = self._extract_inline_data(
                task
            )

            if inline_data:

                try:

                    analysis = self._analyze_inline_data(
                        inline_data
                    )

                except Exception as error:

                    return (
                        "Inline data analysis failed.\n"
                        f"Error: {error}"
                    )

        # -----------------------------------------------------
        # PREPARE DATA CONTEXT
        # -----------------------------------------------------

        if analysis:

            data_context = str(
                analysis
            )

        else:

            data_context = (
                "No structured CSV, Excel, or inline "
                "dataset was detected. Do not invent data."
            )

        # -----------------------------------------------------
        # LLM INTERPRETATION
        # -----------------------------------------------------

        prompt = f"""
You are CHORUS's Data Analyst Agent.

Complete ONLY the data-analysis task below.

ASSIGNED TASK:
{task}

ACTUAL DATA ANALYSIS:
{data_context}

IMPORTANT:

The ACTUAL DATA ANALYSIS section contains calculations
performed by CHORUS locally.

Use those calculations as the source of truth.

RULES:

1. Never invent numbers.
2. Never invent rows or records.
3. Never invent statistics.
4. Never contradict the actual data analysis.
5. Use the calculated totals, averages, minimums,
   maximums, and growth percentages when available.
6. Identify meaningful patterns and trends only when
   supported by the data.
7. Identify anomalies only when supported by the data.
8. Clearly distinguish observations from assumptions.
9. Keep recommendations directly connected to the data.
10. If no dataset is available, clearly explain what
    data is required.
11. Do not perform unrelated tasks.
12. Keep the response concise and useful.

If the user explicitly requested a calculation and the
calculated value exists in ACTUAL DATA ANALYSIS, include it
clearly in the response.

RETURN:

DATA SUMMARY
<concise summary of the dataset and requested calculations>

KEY FINDINGS
• <finding>
• <finding>
• <finding>

PATTERNS AND TRENDS
• <supported pattern>
• <supported pattern>

DATA QUALITY
<important data-quality observations, or None identified>

ANOMALIES
<supported anomalies, or None identified>

INSIGHTS
• <insight>
• <insight>

RECOMMENDATIONS
• <recommendation>
• <recommendation>
"""

        # -----------------------------------------------------
        # CENTRALIZED LLM HANDLER
        # -----------------------------------------------------

        response = self.invoke(
            prompt
        )

        # -----------------------------------------------------
        # NORMALIZE RESPONSE
        # -----------------------------------------------------

        content = response.content

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
                        item["text"]
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
    # DATA FILE DETECTION
    # =========================================================

    @staticmethod
    def _find_data_file(
        task: str
    ):
        """
        Find a CSV or Excel file explicitly provided
        in the task.

        Supports attachment context such as:

            FILE 1: sales_data.csv
            TYPE: text/csv
            FILE_PATH: C:\\project\\uploads\\abc_sales_data.csv

        The explicit FILE_PATH/PATH handling is important
        because Windows paths can contain spaces.
        """

        if not task:
            return None

        extensions = {
            ".csv",
            ".xlsx",
            ".xls",
        }

        # =====================================================
        # METHOD 1 — EXPLICIT FILE_PATH
        # =====================================================

        explicit_paths = re.findall(
            r"(?im)^\s*(?:FILE_PATH|PATH)\s*:\s*(.+?)\s*$",
            task,
        )

        for raw_path in explicit_paths:

            candidate = (
                raw_path
                .strip()
                .strip('"')
                .strip("'")
            )

            if not candidate:
                continue

            path = Path(
                candidate
            )

            if (
                path.exists()
                and path.is_file()
                and path.suffix.lower()
                in extensions
            ):

                print(
                    "[DATA ANALYST] Explicit file found:",
                    path
                )

                return str(
                    path
                )

        # =====================================================
        # METHOD 2 — WINDOWS / UNIX PATHS EMBEDDED IN TEXT
        # =====================================================

        path_patterns = [
            # Windows absolute path
            r'(?i)([A-Za-z]:\\[^"\n\r]+?\.(?:csv|xlsx|xls))',

            # Windows path with forward slashes
            r'(?i)([A-Za-z]:/[^"\n\r]+?\.(?:csv|xlsx|xls))',

            # Unix absolute path
            r'(/[^\n\r"]+?\.(?:csv|xlsx|xls))',
        ]

        for pattern in path_patterns:

            matches = re.findall(
                pattern,
                task
            )

            for raw_path in matches:

                candidate = (
                    raw_path
                    .strip()
                    .strip('"')
                    .strip("'")
                    .rstrip(".,;:()[]{}<>")
                )

                path = Path(
                    candidate
                )

                if (
                    path.exists()
                    and path.is_file()
                    and path.suffix.lower()
                    in extensions
                ):

                    print(
                        "[DATA ANALYST] Path-based file found:",
                        path
                    )

                    return str(
                        path
                    )

        # =====================================================
        # METHOD 3 — INDIVIDUAL WORDS
        # =====================================================

        cleaned_task = (
            task
            .replace('"', "")
            .replace("'", "")
        )

        words = cleaned_task.split()

        for word in words:

            candidate = word.strip(
                ".,;:()[]{}<>"
            )

            path = Path(
                candidate
            )

            if (
                path.suffix.lower()
                in extensions
                and path.exists()
                and path.is_file()
            ):

                print(
                    "[DATA ANALYST] Filename found:",
                    path
                )

                return str(
                    path
                )

        return None

    # =========================================================
    # INLINE DATA EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_inline_data(
        task: str
    ):
        """
        Extract structured data directly from the user's
        natural-language request.

        Supported formats:

            Month,Sales
            January,120000
            February,135000

        Or:

            January - ₹120,000
            February - ₹135,000

        Or:

            January: ₹120,000
            February: ₹135,000

        Or:

            January ₹120,000
            February ₹135,000
        """

        # -----------------------------------------------------
        # NORMALIZE TEXT
        # -----------------------------------------------------

        normalized_task = (
            task
            .replace("\u00a0", " ")
            .strip()
        )

        # =====================================================
        # METHOD 1 — MULTILINE CSV
        # =====================================================

        lines = [
            line.strip()
            for line in normalized_task.splitlines()
            if line.strip()
        ]

        csv_candidates = []

        for line in lines:

            if "," not in line:
                continue

            parts = [
                part.strip()
                for part in line.split(",")
            ]

            if len(parts) >= 2:

                csv_candidates.append(
                    parts
                )

        if len(csv_candidates) >= 2:

            column_count = len(
                csv_candidates[0]
            )

            rows = [
                row
                for row in csv_candidates
                if len(row) == column_count
            ]

            if len(rows) >= 2:

                return rows

        # =====================================================
        # METHOD 2 — MONTH / VALUE PAIRS
        # =====================================================

        months = (
            "January|February|March|April|May|June|"
            "July|August|September|October|November|December"
        )

        number = (
            r"(?:₹|\$|€|£)?\s*"
            r"[-+]?"
            r"\d+(?:,\d{3})*(?:\.\d+)?"
        )

        month_pattern = (
            r"\b("
            + months
            + r")\b"
            r"\s*"
            r"(?:-|–|—|:|\bis\b)?"
            r"\s*"
            r"("
            + number
            + r")"
        )

        month_matches = re.findall(
            month_pattern,
            normalized_task,
            flags=re.IGNORECASE
        )

        if len(month_matches) >= 2:

            rows = [
                ["Month", "Sales"]
            ]

            for month, value in month_matches:

                clean_value = (
                    value
                    .replace(",", "")
                    .replace("₹", "")
                    .replace("$", "")
                    .replace("€", "")
                    .replace("£", "")
                    .strip()
                )

                rows.append([
                    month.capitalize(),
                    clean_value
                ])

            return rows

        # =====================================================
        # METHOD 3 — GENERIC LABEL / VALUE PAIRS
        # =====================================================

        generic_pattern = (
            r"\b([A-Za-z][A-Za-z\s]{1,30}?)\b"
            r"\s*(?:-|–|—|:|\bis\b)"
            r"\s*"
            r"(?:₹|\$|€|£)?\s*"
            r"([-+]?\d+(?:,\d{3})*(?:\.\d+)?)"
        )

        generic_matches = re.findall(
            generic_pattern,
            normalized_task,
            flags=re.IGNORECASE
        )

        if len(generic_matches) >= 2:

            rows = [
                ["Category", "Value"]
            ]

            for label, value in generic_matches:

                clean_label = (
                    label
                    .strip()
                    .strip("-–—:")
                )

                clean_value = (
                    value
                    .replace(",", "")
                    .strip()
                )

                rows.append([
                    clean_label,
                    clean_value
                ])

            return rows

        return None

    # =========================================================
    # INLINE DATA ANALYSIS
    # =========================================================

    @staticmethod
    def _analyze_inline_data(
        rows
    ):
        """
        Perform deterministic local analysis on inline data.

        Arithmetic is performed locally rather than relying
        on the LLM.
        """

        if not rows or len(rows) < 2:
            return None

        # -----------------------------------------------------
        # HEADERS
        # -----------------------------------------------------

        headers = [
            str(header).strip()
            for header in rows[0]
        ]

        # -----------------------------------------------------
        # DATA ROWS
        # -----------------------------------------------------

        data_rows = []

        for row in rows[1:]:

            cleaned_row = [
                str(value).strip()
                for value in row
            ]

            data_rows.append(
                cleaned_row
            )

        # -----------------------------------------------------
        # FIND NUMERIC COLUMNS
        # -----------------------------------------------------

        numeric_columns = {}

        for column_index, header in enumerate(
            headers
        ):

            values = []

            value_rows = []

            for row in data_rows:

                if column_index >= len(row):
                    continue

                raw_value = row[
                    column_index
                ]

                cleaned = (
                    raw_value
                    .replace(",", "")
                    .replace("₹", "")
                    .replace("$", "")
                    .replace("€", "")
                    .replace("£", "")
                    .replace("%", "")
                    .strip()
                )

                try:

                    value = float(
                        cleaned
                    )

                    values.append(
                        value
                    )

                    value_rows.append(
                        row
                    )

                except ValueError:

                    continue

            # -------------------------------------------------
            # ONLY PROCESS NUMERIC COLUMNS
            # -------------------------------------------------

            if not values:
                continue

            total = sum(
                values
            )

            average = (
                total / len(values)
            )

            minimum = min(
                values
            )

            maximum = max(
                values
            )

            minimum_index = values.index(
                minimum
            )

            maximum_index = values.index(
                maximum
            )

            # -------------------------------------------------
            # FIRST / LAST VALUES
            # -------------------------------------------------

            first_value = values[0]

            last_value = values[-1]

            # -------------------------------------------------
            # OVERALL GROWTH
            # -------------------------------------------------

            if first_value != 0:

                overall_growth = (
                    (
                        last_value
                        - first_value
                    )
                    / first_value
                ) * 100

            else:

                overall_growth = None

            # -------------------------------------------------
            # LABELS
            # -------------------------------------------------

            minimum_label = None
            maximum_label = None
            first_label = None
            last_label = None

            if value_rows:

                if minimum_index < len(
                    value_rows
                ):

                    if value_rows[
                        minimum_index
                    ]:

                        minimum_label = (
                            value_rows[
                                minimum_index
                            ][0]
                        )

                if maximum_index < len(
                    value_rows
                ):

                    if value_rows[
                        maximum_index
                    ]:

                        maximum_label = (
                            value_rows[
                                maximum_index
                            ][0]
                        )

                if value_rows[0]:

                    first_label = (
                        value_rows[0][0]
                    )

                if value_rows[-1]:

                    last_label = (
                        value_rows[-1][0]
                    )

            # -------------------------------------------------
            # COLUMN RESULT
            # -------------------------------------------------

            analysis_entry = {
                "count": len(values),
                "total": total,
                "average": average,
                "minimum": minimum,
                "maximum": maximum,
                "minimum_row": (
                    minimum_index + 1
                ),
                "maximum_row": (
                    maximum_index + 1
                ),
                "minimum_label": (
                    minimum_label
                ),
                "maximum_label": (
                    maximum_label
                ),
                "first_value": (
                    first_value
                ),
                "last_value": (
                    last_value
                ),
                "first_label": (
                    first_label
                ),
                "last_label": (
                    last_label
                ),
                "overall_growth_percentage": (
                    overall_growth
                ),
            }

            # -------------------------------------------------
            # MONTH-TO-MONTH CHANGES
            # -------------------------------------------------

            if len(values) >= 2:

                percentage_changes = []

                for index in range(
                    1,
                    len(values)
                ):

                    previous = values[
                        index - 1
                    ]

                    current = values[
                        index
                    ]

                    if previous == 0:

                        change = None

                    else:

                        change = (
                            (
                                current
                                - previous
                            )
                            / previous
                        ) * 100

                    percentage_changes.append(
                        change
                    )

                analysis_entry[
                    "percentage_changes"
                ] = percentage_changes

            else:

                analysis_entry[
                    "percentage_changes"
                ] = []

            # -------------------------------------------------
            # STORE COLUMN RESULT
            # -------------------------------------------------

            numeric_columns[
                header
            ] = analysis_entry

        # -----------------------------------------------------
        # BUILD FINAL RESULT
        # -----------------------------------------------------

        result = {
            "rows": len(data_rows),
            "columns": headers,
            "numeric_columns": numeric_columns,
            "data": rows,
        }

        return result