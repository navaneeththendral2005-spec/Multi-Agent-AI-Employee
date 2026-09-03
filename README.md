# CHORUS — Multi-Agent AI Employee

CHORUS is an AI-powered multi-agent employee system designed to understand user requests, coordinate specialized AI agents, and execute tasks across software development, research, data analysis, document generation, and communication.

Instead of relying on a single AI model for every task, CHORUS uses specialized agents coordinated through a central Manager and Orchestrator.

---

## Overview

CHORUS can handle a wide range of tasks through specialized agents, including:

- Software development
- Web research
- Data analysis
- Document generation
- Presentation generation
- Spreadsheet generation
- File processing
- Email communication
- Code generation and debugging
- Code review and testing
- Multi-step task orchestration

The system is designed around the idea of an AI employee that can understand a request, determine the appropriate agent or workflow, execute the task, and return the result through a unified interface.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   CHORUS Frontend    │
                         │     React + Vite     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │   Manager / Orchestrator     │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
   Research Agent          Data Analyst Agent       Document Agent
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              Developer       Code Fixer    Communication
                Agent           Agent           Agent

## Project Structure

Multi-Agent-AI-Employee/
│
├── agents/
│   ├── manager_agent.py
│   ├── orchestrator.py
│   ├── research_agent.py
│   ├── data_analyst_agent.py
│   ├── document_agent.py
│   ├── developer_agent.py
│   ├── backend_agent.py
│   ├── code_generator_agent.py
│   ├── code_fixer_agent.py
│   ├── debugger_agent.py
│   ├── code_reviewer_agent.py
│   ├── communication_agent.py
│   ├── content_agent.py
│   └── tester_agent.py
│
├── api/
│   └── server.py
│
├── communication_auth/
│   └── gmail_auth.py
│
├── document_tools/
│   └── creator.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── data/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── workspace/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md