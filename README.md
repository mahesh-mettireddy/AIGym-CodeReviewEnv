# CodeReviewEnv

An OpenEnv reinforcement learning environment where AI agents learn to review Python code like a senior developer.

## Motivation

Code review is a real-world task performed daily by developers. Training agents to identify bugs, code smells, and suggest improvements has direct practical value for AI-assisted development tools.

## Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| bug_detection | Easy | Identify if the code has a bug and explain it |
| code_smell | Medium | Identify bad practices like magic numbers, bare excepts |
| improvement | Hard | Suggest a specific, actionable improvement |

## Action Space

| Field | Type | Description |
|-------|------|-------------|
| task | string | Current task name |
| verdict | string | Agent's review verdict |
| confidence | float | Agent confidence 0.0–1.0 |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| task | string | Current task name |
| code_snippet | string | Python code to review |
| instruction | string | What the agent must do |
| last_verdict | string | Agent's previous verdict |
| last_reward | float | Reward from last step |
| done | boolean | Episode complete |
| score | float | Total score so far |
| feedback | string | Feedback on last action |

## Reward Function

- Exact correct identification with explanation → 1.0
- Correct verdict, weak explanation → 0.6
- Partially correct → 0.3–0.4
- Wrong → 0.0

## Setup
```bash
pip install openenv-core
python inference.py
```

## Baseline Scores

| Task | Baseline Score |
|------|---------------|
| bug_detection | ~0.8 |
| code_smell | ~0.6 |
| improvement | ~0.5 |

## Environment Variables

| Variable | Description |
|----------|-------------|
| API_BASE_URL | LLM API endpoint |
| MODEL_NAME | Model identifier |
| HF_TOKEN | HuggingFace API key |