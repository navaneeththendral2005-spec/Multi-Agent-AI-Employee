"""Display metadata for registered agents. Keys match AgentRegistry names."""

AGENT_META = {
    "manager": {
        "label": "Manager",
        "icon": "◆",
        "role": "Plans work and assigns specialists",
    },
    "developer": {
        "label": "Developer",
        "icon": "</>",
        "role": "Application design and implementation",
    },
    "backend": {
        "label": "Backend",
        "icon": "⬡",
        "role": "APIs, services, and data layers",
    },
    "code_generator": {
        "label": "Code Generator",
        "icon": "⌘",
        "role": "Produces project source files",
    },
    "research": {
        "label": "Research",
        "icon": "◎",
        "role": "Investigation and synthesis",
    },
    "content": {
        "label": "Content",
        "icon": "✎",
        "role": "Writing and editorial work",
    },
    "data": {
        "label": "Data Analyst",
        "icon": "▣",
        "role": "Datasets, metrics, and reports",
    },
    "document": {
        "label": "Document",
        "icon": "▤",
        "role": "Document reading and creation",
    },
    "communication": {
        "label": "Communication",
        "icon": "✉",
        "role": "Email and stakeholder updates",
    },
    "tester": {
        "label": "Tester",
        "icon": "✓",
        "role": "Test execution and reporting",
    },
    "debugger": {
        "label": "Debugger",
        "icon": "⚑",
        "role": "Failure analysis and root cause",
    },
    "code_reviewer": {
        "label": "Code Reviewer",
        "icon": "▣",
        "role": "Review quality and correctness",
    },
    "code_fixer": {
        "label": "Code Fixer",
        "icon": "⚒",
        "role": "Applies targeted code fixes",
    },
    "browser": {
        "label": "Browser",
        "icon": "◉",
        "role": "Web browsing and page tasks",
    },
}


def agent_label(name: str) -> str:
    meta = AGENT_META.get(name.lower())
    if meta:
        return meta["label"]
    return name.replace("_", " ").title()


def agent_icon(name: str) -> str:
    meta = AGENT_META.get(name.lower())
    return meta["icon"] if meta else "●"


def agent_role(name: str) -> str:
    meta = AGENT_META.get(name.lower())
    return meta["role"] if meta else "Specialist agent"
