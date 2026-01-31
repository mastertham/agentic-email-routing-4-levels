# Agentic Email Routing — 4 Levels (Python)

One use case: **Email routing** (Sales/Support/Billing/Security/HR).

This repo demonstrates 4 maturity levels:

1) **Level 1 — RPA + AI action**
   - Fixed steps: classify -> summarize -> route

2) **Level 2 — Orchestrated workflow agent**
   - Still fixed steps, but adds branching + guardrails:
     - extract entities
     - ask for more info if confidence low / missing info

3) **Level 3 — ReAct agent**
   - Agent chooses which tool to call next and loops until it can stop
   - You provide tools + stop condition + max steps

4) **Level 4 — Planning agent**
   - Agent creates an explicit plan first, then executes
   - Plan can change based on risk (e.g., security incident routes fast)

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py
