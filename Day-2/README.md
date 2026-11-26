# Day 2 — Prompts, Memory & Python Basics for Agents

## Overview
Upgraded the Sweet Crumbs assistant into a multi-turn chatbot with structured prompt design (Role · Facts · Rules · Format), conversation history trimming, and safe error handling.

## Topics Covered
- Message roles: `system`, `user`, `assistant`
- System prompt structure (`ROLE`, `FACTS`, `RULES`, `FORMAT`)
- Few-shot examples & structured JSON outputs (`json.dumps`, `json.loads`)
- Conversation memory loop with `MAX_TURNS` trimming
- Python essentials for agents: dicts, functions with type hints & docstrings, decorators (`@log_call`), and `try/except`

## Files
- `task.py` — Multi-turn chatbot with `MENU`, `get_price` + `@log_call`, and `RateLimitError`/`APIConnectionError` handling
- `Day-02.ipynb` — Google Colab notebook for Day 2
- `.env.example` — Environment variable template (`GROQ_API_KEY`)

## How to Run
```bash
pip install openai
export GROQ_API_KEY="your_groq_api_key"
python task.py
```
