"""
File upload panel.

Reads uploads with document_tools.reader.read_file() and stores extracted
text in session state so the existing workflow can receive it as request
context. File-processing logic in the backend is not changed.
"""

import html
import os
import tempfile

import streamlit as st

from document_tools.reader import read_file

SUPPORTED_TYPES = [
    "pdf",
    "docx",
    "doc",
    "pptx",
    "ppt",
    "csv",
    "xlsx",
    "xls",
    "txt",
]

FILE_ICONS = {
    ".pdf": "PDF",
    ".docx": "DOC",
    ".doc": "DOC",
    ".pptx": "PPT",
    ".ppt": "PPT",
    ".csv": "CSV",
    ".xlsx": "XLS",
    ".xls": "XLS",
    ".txt": "TXT",
}


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def render_composer_upload(key_suffix: str = "primary") -> None:
    """Render the attachment control used inside the request composer."""
    uploaded = st.file_uploader(
        "Upload files",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        key=f"workspace_file_uploader_{key_suffix}",
        label_visibility="collapsed",
    )

    _store_uploaded_files(uploaded)


def render_file_upload() -> None:
    """Render the sidebar attached-file list."""
    st.markdown('<div class="nav-label">Attachments</div>', unsafe_allow_html=True)

    if "uploaded_files_data" not in st.session_state:
        st.session_state.uploaded_files_data = []

    files_data = st.session_state.uploaded_files_data
    if files_data:
        for file_info in files_data:
            ext = os.path.splitext(file_info["name"])[1].lower()
            kind = FILE_ICONS.get(ext, "FILE")
            name = html.escape(file_info["name"])
            size_str = _format_size(file_info["size"])
            st.markdown(
                f"""
                <div class="file-chip">
                    <span>{html.escape(kind)} · {name}</span>
                    <span class="meta">{size_str}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Clear attachments", key="clear_files_btn", use_container_width=True):
            st.session_state.uploaded_files_data = []
            st.rerun()
    else:
        st.caption("Attach files from the request box.")


def _store_uploaded_files(uploaded) -> None:
    """Read new uploaded files into session state."""
    if "uploaded_files_data" not in st.session_state:
        st.session_state.uploaded_files_data = []

    if not uploaded:
        return

    current_names = {item["name"] for item in st.session_state.uploaded_files_data}
    for file in uploaded:
        if file.name in current_names:
            continue
        content = _read_uploaded_file(file)
        if content is not None:
            st.session_state.uploaded_files_data.append(
                {
                    "name": file.name,
                    "size": file.size,
                    "content": content,
                }
            )


def _read_uploaded_file(uploaded_file) -> str | None:
    """Persist the upload to a temp file and read it with the existing reader."""
    try:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()
        if suffix in {".doc", ".ppt"}:
            st.error(
                f"**{uploaded_file.name}** is a legacy Office format. "
                "The current document reader supports .docx and .pptx. "
                "Please convert the file and upload again."
            )
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            return read_file(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as error:
        st.error(f"Could not read **{uploaded_file.name}**. {error}")
        return None


def build_augmented_request(user_request: str) -> str:
    """Append extracted attachment text to the user request."""
    files_data = st.session_state.get("uploaded_files_data", [])
    if not files_data:
        return user_request

    file_sections = [
        f"--- ATTACHED FILE: {item['name']} ---\n{item['content']}\n--- END OF FILE ---"
        for item in files_data
    ]
    files_text = "\n\n".join(file_sections)
    return f"{user_request}\n\nDOCUMENT CONTEXT / ATTACHMENTS:\n\n{files_text}"


def get_attached_file_names() -> list:
    """Return names of files attached to the next request."""
    files_data = st.session_state.get("uploaded_files_data", [])
    return [item["name"] for item in files_data]
