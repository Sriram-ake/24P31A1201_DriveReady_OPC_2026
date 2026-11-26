# Day 4 — Tools, Structured Output & Google Sheets

## Overview
Upgraded the Sweet Crumbs Home Bakery assistant into a tool-using AI agent using LangChain (`@tool`, `create_agent`), Pydantic (`BaseModel`) validation, rate-limit/error resilience, and live Google Sheets order logging (`gspread`).

## Key Concepts & Implementation
1. **Why Agents Need Tools & Function Calling:**
   - LLMs generate text from training data and prompt context; tools allow them to fetch live facts (menu prices, timings), perform exact arithmetic, and take actions (saving orders).
   - The model outputs a structured **tool call** (function name + arguments), Python executes the function, and the result is returned as a `tool` message in the agent loop.
2. **Custom Tools (`@tool`):**
   - `get_price(item, qty)` — Computes exact rupee totals from the bakery menu and returns a polite message for off-menu items.
   - `is_open(day)` — Checks daily bakery opening hours.
   - `log_order(name, item, qty, date, eggless)` — Validates order fields and saves confirmed orders to Google Sheets.
3. **Structured Output with Pydantic (`Order` Schema):**
   - Defined `Order(BaseModel)` enforcing valid menu items (`Literal["plum cake", "chocolate cake", "cupcake"]`), positive quantities (`ge=1`), customer name, pickup date, and eggless preference before saving.
4. **Agent Execution & Error Handling (`create_agent`):**
   - Built `create_agent(model=ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=3), tools=[get_price, is_open, log_order], system_prompt=SYSTEM)`.
   - Handled rate limits (`429`) and runtime errors gracefully with `try/except` and inspected execution traces via `m.pretty_print()`.
5. **Live Database with Google Sheets (`gspread`):**
   - Authenticated Google Colab via `google.colab.auth` + `gspread`, initialized `Sweet Crumbs Orders` with columns `["name", "item", "qty", "date", "eggless", "total"]`, and logged confirmed rows via `ws.append_row(...)`.

## Files
- `Day-04.ipynb` — Google Colab notebook with Google Sheets setup, Pydantic `Order` model, `@tool` functions, `create_agent` chat demo, and trace inspection
- `task.py` — Standalone Python script for the Day 4 tool-calling bakery agent
- `.env.example` — Environment variable template (`GROQ_API_KEY`)

## How to Run in Google Colab
1. Open `Day-04.ipynb` in Google Colab.
2. Open the **Secrets** tab (key icon in the left sidebar), add `GROQ_API_KEY`, and enable **Notebook access**.
3. Run Cells 1–4 in order and complete the Google sign-in prompt for `gspread` when asked.