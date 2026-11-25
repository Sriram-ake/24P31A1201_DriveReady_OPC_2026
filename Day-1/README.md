# Day 1 — How LLMs Work & Your First API Call

## Overview
Built the first LLM-powered response script for **Sweet Crumbs Home Bakery** using the Groq API (`GROQ_API_KEY` stored in Google Colab Secrets).

## Topics Covered
- How LLMs predict the next token in a loop
- Tokens, temperature (`0.2` for factual replies vs higher values for creative text), and context windows
- Stateless API calls and preventing hallucination with prompt facts
- Calling Groq via the `openai` Python client (`base_url="https://api.groq.com/openai/v1"`) and `langchain-groq`

## Files
- `task.py` — First API call script with Sweet Crumbs `SYSTEM` prompt and token usage output
- `Day-01.ipynb` — Google Colab notebook for Day 1 experiments
- `.env.example` — Environment variable template (`GROQ_API_KEY`)

## How to Run
```bash
pip install openai
export GROQ_API_KEY="your_groq_api_key"
python task.py
```
