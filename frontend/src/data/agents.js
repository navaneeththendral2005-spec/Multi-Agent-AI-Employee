// =========================================================
// AGENT ROSTER
// =========================================================

export const AGENTS = [
  {
    id: 'orchestrator',
    name: 'Orchestrator',
    role: 'Routes requests and reports back',
    color: 'var(--color-agent-orchestrator)',
    initial: 'O',
  },

  {
    id: 'research',
    name: 'Researcher',
    role: 'Finds and verifies sources',
    color: 'var(--color-agent-research)',
    initial: 'R',
  },

  {
    id: 'code',
    name: 'Coder',
    role: 'Writes and tests code',
    color: 'var(--color-agent-code)',
    initial: 'C',
  },

  {
    id: 'writing',
    name: 'Writer',
    role: 'Drafts and edits copy',
    color: 'var(--color-agent-writing)',
    initial: 'W',
  },
]


// =========================================================
// QUICK PROMPTS
// =========================================================

export const QUICK_PROMPTS = [
  {
    text: 'Help me plan my day in three steps',
    agentId: 'orchestrator',
  },

  {
    text: 'Make this message sound warm and clear',
    agentId: 'writing',
  },

  {
    text: 'Explain a tricky idea in simple words',
    agentId: 'research',
  },
]


// =========================================================
// AGENT TICKER
// =========================================================

export const AGENT_TICKER_NAMES = [
  'Manager Agent',
  'Developer Agent',
  'Backend Agent',
  'Code Generator Agent',
  'Tester Agent',
  'Debugger Agent',
  'Code Fixer Agent',
  'Code Reviewer Agent',
  'Research Agent',
  'Content Agent',
  'Data Analyst Agent',
  'Document Agent',
  'Communication Agent',
]