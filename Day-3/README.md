# Day 3 — Your First AI Agent & LangChain

## Overview
Rebuilt the **Sweet Crumbs Home Bakery** assistant using **LangChain** (`ChatGroq`, `ChatPromptTemplate`, `MessagesPlaceholder`, `StrOutputParser`), added automated regression evaluation via `tests.csv`, explored `create_agent`, and prepared typed Python functions for Day 4 tools.

## What Was Implemented
1. **LangChain Chain (`prompt | llm | StrOutputParser()`):**
   - Uses `ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)` with `GROQ_API_KEY` loaded from Colab Secrets (`userdata.get("GROQ_API_KEY")`).
   - Maintains multi-turn conversation memory using `MessagesPlaceholder("history")`.
2. **Automated Evaluation (`tests.csv`):**
   - **Initial Prompt (v1):** Scored **3/5 (60%)** — failed on same-day notice (`"I'll check with the owner"` instead of `"24 hours"`) and formatting (`"egg-less"` instead of `"eggless"`).
   - **Improved Prompt (v2):** Clarified the 24-hour notice rule for same-day orders, restricted `"I'll check with the owner."` to out-of-scope questions, and standardized `"eggless"`. Expanded `tests.csv` to 10 real customer questions.
3. **Temperature Experiment (`temperature=1.0`):**
   - Higher temperature introduces wording variations between runs (sometimes changing exact keyword matches), confirming why customer-support / pricing assistants should stay at low temperature (`0.0–0.3`).
4. **Agent Sneak Peek (`create_agent`):**
   - Initialized `create_agent(model=llm, tools=[], system_prompt=SYSTEM)` ahead of attaching tools on Day 4.
5. **Agent or Not? (Business Task Breakdown):**
   - **Calculate order total (`qty × price`)** → **Plain code** (fixed math, must be exact)
   - **Write a festival offer caption** → **One LLM call** (single creative text generation)
   - **Handle an unstructured customer order, check availability, compute price, and log it** → **Agent** (dynamic steps + tools)
6. **Day 4 Prep Functions:**
   - `get_price(item: str, qty: int = 1) -> str`
   - `check_availability(item: str, hours_notice: int = 24) -> str`

## Files
- `task.py` — Complete Day 3 LangChain script, test runner, `create_agent` demo, and Day 4 prep functions
- `Day-03.ipynb` — Google Colab notebook for Day 3
- `tests.csv` — 10 customer test cases with `must_include` assertions
- `.env.example` — Environment variable template (`GROQ_API_KEY`)

## How to Run in Google Colab
1. Open `Day-03.ipynb` in Google Colab.
2. Open the **Secrets** tab (key icon in the left sidebar), add `GROQ_API_KEY`, and turn on **Notebook access**.
3. Run Cells 1–8 in order.

## How to Run Locally
```bash
pip install langchain langchain-groq
export GROQ_API_KEY="your_groq_api_key"
python task.py
```
