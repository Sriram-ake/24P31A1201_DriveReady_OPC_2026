# Day 4 — Tools, Structured Output & Google Sheets

## Overview
Upgraded the **Sweet Crumbs Home Bakery** assistant into a tool-using AI agent using LangChain (`@tool`, `create_agent`), added Pydantic (`BaseModel`) schema validation for incoming orders, implemented rate-limit and error handling, and connected live order logging to Google Sheets via `gspread`.

## What Was Implemented
1. **Custom Tools & Function Calling (`@tool`):**
  - `get_price(item: str, qty: int = 1) -> str` — Computes exact rupee totals from `MENU` and returns a polite list of available items if an off-menu item is requested.
  - `is_open(day: str) -> str` — Checks daily bakery opening hours from `HOURS` and validates day names.
  - `log_order(name: str, item: str, qty: int, date: str, eggless: bool) -> str` — Validates order fields via Pydantic and saves confirmed orders to Google Sheets.
2. **Structured Output with Pydantic (`Order` Schema):**
  - Defined `Order(BaseModel)` enforcing `item: Literal["plum cake", "chocolate cake", "cupcake"]`, `qty: int` (`ge=1`), `name: str`, `date: str`, and `eggless: bool` so invalid or incomplete orders never reach the spreadsheet.
3. **Tool-Using Agent & Trace Inspection (`create_agent`):**
  - Configured `create_agent(model=llm, tools=[get_price, is_open, log_order], system_prompt=SYSTEM)` using `ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=3)`.
  - Verified multi-turn tool execution and inspected the full message trace (`m.pretty_print()`) across user prompts, tool calls, tool outputs, and final replies.
4. **Rate Limits & Error Handling:**
  - Handled HTTP `429 Too Many Requests` retries with `max_retries=3` on `ChatGroq` and wrapped `agent.invoke()` in `try/except` to return a polite fallback message on transient API errors.
5. **Live Order Logging with Google Sheets (`gspread`):**
  - Authenticated Colab via `google.colab.auth` + `gspread`, initialized the `Sweet Crumbs Orders` spreadsheet with headers `["name", "item", "qty", "date", "eggless", "total"]`, and logged confirmed orders with `ws.append_row(...)`.
6. **Edge-Case Validation Checks:**
  - *Off-menu item (e.g., `"donut"`)* → Rejected by `get_price` / `Order` validation with available menu items.
  - *Incomplete order (missing name or pickup date)* → Agent asks for missing details before calling `log_order`.
  - *Invalid quantity (`0`)* → Blocked by Pydantic `ge=1` validation before writing to Google Sheets.

## Files
- `task.py` — Complete Day 4 tool-calling bakery agent script with Pydantic validation and Google Sheets integration
- `Day-04.ipynb` — Google Colab notebook for Day 4
- `.env.example` — Environment variable template (`GROQ_API_KEY`)

## How to Run in Google Colab
1. Open `Day-04.ipynb` in Google Colab.
2. Open the **Secrets** tab (key icon in the left sidebar), add `GROQ_API_KEY`, and turn on **Notebook access**.
3. Run the cells in order and complete the Google sign-in prompt for `gspread` when asked.

## How to Run Locally
```bash
pip install langchain langchain-groq gspread pydantic
export GROQ_API_KEY="your_groq_api_key"
python task.py
