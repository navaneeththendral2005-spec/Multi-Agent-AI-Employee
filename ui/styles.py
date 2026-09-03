"""
Shared stylesheet for the Multi-Agent AI Employee Streamlit workspace.

The active interface is intentionally dark, quiet, and OpenAI-inspired:
pitch-black canvas, white typography, restrained borders, and glassy
composer surfaces.
"""

import streamlit as st

DARK_VARS = """
    --bg-app: #000000;
    --bg-sidebar: rgba(8, 8, 8, 0.94);
    --bg-elevated: rgba(20, 20, 20, 0.72);
    --bg-card: rgba(255, 255, 255, 0.055);
    --bg-input: rgba(255, 255, 255, 0.04);
    --bg-hover: rgba(255, 255, 255, 0.09);
    --bg-user: rgba(255, 255, 255, 0.10);
    --border: rgba(255, 255, 255, 0.10);
    --border-strong: rgba(255, 255, 255, 0.18);
    --text: #FFFFFF;
    --text-secondary: #C9C9C9;
    --text-muted: #858585;
    --accent: #10A37F;
    --accent-strong: #14B889;
    --accent-soft: rgba(16, 163, 127, 0.14);
    --danger: #FF7B7B;
    --danger-soft: rgba(255, 123, 123, 0.12);
    --shadow: 0 22px 60px rgba(0, 0, 0, 0.48);
    --glass-blur: blur(22px) saturate(140%);
    --radius: 14px;
    --radius-sm: 8px;
    --radius-lg: 28px;
    --font: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
"""

LIGHT_VARS = DARK_VARS

SHARED_CSS = """
.stApp {
    background: var(--bg-app) !important;
    color: var(--text);
    font-family: var(--font);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: linear-gradient(to bottom, transparent, #000 20%, #000 78%, transparent);
}

[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    position: relative;
    z-index: 1;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    display: none;
}

#MainMenu, footer, [data-testid="stDecoration"] {
    visibility: hidden;
    display: none;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 4.5rem !important;
    max-width: 1060px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0.75rem 0.75rem 1.2rem 0.75rem;
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 8px 16px 8px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

.brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #FFFFFF;
    color: #000000;
    font-weight: 750;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    letter-spacing: 0;
}

.brand-name {
    font-size: 15.5px;
    font-weight: 650;
    color: var(--text);
    letter-spacing: 0;
}

.brand-sub {
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 1px;
}

.nav-label {
    font-size: 10.5px;
    font-weight: 650;
    letter-spacing: 0;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 14px 8px 6px 8px;
}

.agent-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
}

.agent-row.active {
    background: var(--accent-soft);
    border-color: rgba(16, 163, 127, 0.26);
}

.agent-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--text-muted);
    margin-top: 6px;
    flex-shrink: 0;
}

.agent-dot.on {
    background: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
}

.agent-name {
    font-size: 13px;
    color: var(--text);
    font-weight: 600;
}

.agent-role {
    font-size: 11px;
    color: var(--text-muted);
    line-height: 1.35;
    margin-top: 1px;
}

.file-chip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 7px 10px;
    margin-bottom: 6px;
    font-size: 12.5px;
    color: var(--text);
}

.file-chip span.meta {
    color: var(--text-muted);
    font-size: 11px;
    white-space: nowrap;
}

.workspace-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 4px 16px 4px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}

.workspace-title {
    font-size: 15px;
    font-weight: 620;
    color: var(--text);
}

.workspace-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-secondary);
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
}

.status-pill.live {
    border-color: rgba(16, 163, 127, 0.38);
    background: var(--accent-soft);
    color: var(--text);
}

.pulse {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent);
}

.hero {
    max-width: 780px;
    margin: 110px auto 24px auto;
    text-align: center;
}

.hero h1 {
    font-size: 32px;
    font-weight: 500;
    letter-spacing: 0;
    margin: 0;
    color: var(--text);
}

.pipeline {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0 14px 0;
}

.pipeline-step {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 600;
}

.pipeline-step.done {
    color: var(--accent-strong);
    border-color: rgba(16, 163, 127, 0.34);
    background: var(--accent-soft);
}

.pipeline-step.current {
    color: var(--text);
    border-color: var(--accent);
    background: var(--accent-soft);
}

.chat-wrap {
    max-width: 820px;
    margin: 0 auto;
    padding: 8px 4px 22px 4px;
}

.msg-meta {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 18px 0 10px 0;
}

.user-bubble {
    max-width: 78%;
    background: var(--bg-user);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 16px;
    border-radius: 18px 18px 6px 18px;
    font-size: 14.5px;
    line-height: 1.55;
    box-shadow: var(--shadow);
    white-space: pre-wrap;
    word-break: break-word;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
}

.ai-row {
    display: flex;
    gap: 12px;
    margin: 8px 0 22px 0;
}

.ai-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #FFFFFF;
    color: #000000;
    font-size: 11px;
    font-weight: 750;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.ai-body {
    flex: 1;
    min-width: 0;
}

.attach-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.attach-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 3px 9px;
    font-size: 12px;
    color: var(--text-secondary);
}

.plan-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    color: var(--text-secondary);
}

.plan-pill {
    background: var(--accent-soft);
    color: var(--accent-strong);
    border: 1px solid rgba(16, 163, 127, 0.26);
    border-radius: 999px;
    padding: 2px 9px;
    font-size: 11.5px;
    font-weight: 650;
    white-space: nowrap;
}

.error-card {
    background: var(--danger-soft);
    border: 1px solid rgba(255, 123, 123, 0.34);
    border-radius: var(--radius);
    padding: 14px 16px;
    color: var(--text);
    margin: 8px 0 16px 0;
}

.error-card h4 {
    margin: 0 0 6px 0;
    color: var(--danger);
    font-size: 14px;
}

.error-card p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 13.5px;
}

[data-testid="stSidebar"] .stButton button {
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    border-color: var(--border-strong) !important;
    background: var(--bg-hover) !important;
    color: var(--text) !important;
}

[data-testid="stForm"] {
    background: rgba(22, 22, 22, 0.58) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow);
    padding: 16px 18px 14px 18px !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
}

[data-testid="stForm"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    box-shadow: none !important;
}

[data-testid="stForm"] textarea::placeholder {
    color: var(--text-muted) !important;
    opacity: 1 !important;
}

[data-testid="stForm"] [data-baseweb="textarea"],
[data-testid="stForm"] [data-baseweb="textarea"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stFormSubmitButton"] button {
    min-height: 38px !important;
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid rgba(255, 255, 255, 0.85) !important;
    border-radius: 999px !important;
    font-weight: 650 !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: #EDEDED !important;
    border-color: #FFFFFF !important;
    color: #000000 !important;
}

.composer-empty {
    min-height: 38px;
}

[data-testid="stForm"] [data-testid="stFileUploader"] {
    margin-top: -2px;
}

[data-testid="stForm"] [data-testid="stFileUploader"] section {
    min-height: 38px !important;
    padding: 0 8px !important;
    background: rgba(255, 255, 255, 0.055) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stForm"] [data-testid="stFileUploader"] section:hover {
    background: var(--bg-hover) !important;
    border-color: var(--border-strong) !important;
}

[data-testid="stForm"] [data-testid="stFileUploader"] button {
    min-height: 28px !important;
    padding: 0 10px !important;
    border-radius: 999px !important;
    background: transparent !important;
    border: none !important;
    color: var(--text) !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
}

[data-testid="stForm"] [data-testid="stFileUploader"] small,
[data-testid="stForm"] [data-testid="stFileUploader"] svg,
[data-testid="stForm"] [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}

[data-testid="stStatus"],
[data-testid="stExpander"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
}

[data-testid="stFileUploader"] section {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-strong) !important;
    border-radius: var(--radius) !important;
}

.stSelectbox, .stToggle {
    margin-bottom: 0.2rem;
}

[data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

.suggestion-column .stButton button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    min-height: 78px !important;
    font-size: 13px !important;
    line-height: 1.4 !important;
    white-space: pre-wrap !important;
    box-shadow: none !important;
}

.suggestion-column .stButton button:hover {
    border-color: var(--border-strong) !important;
    background: var(--bg-hover) !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero {
        margin-top: 72px;
    }

    .hero h1 {
        font-size: 26px;
    }

    .user-bubble {
        max-width: 92%;
    }

    .workspace-bar {
        flex-direction: column;
        align-items: flex-start;
    }
}
"""


def inject_styles(theme: str = "dark") -> None:
    """Inject theme variables and shared dashboard CSS."""
    variables = DARK_VARS if theme == "dark" else LIGHT_VARS
    st.markdown(
        f"<style>:root {{{variables}}}{SHARED_CSS}</style>",
        unsafe_allow_html=True,
    )
