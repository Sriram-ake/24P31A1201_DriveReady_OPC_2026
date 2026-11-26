# 🛠️ Day 4: Tools, Structured Records, Sheets & Agent Traces

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Sriram-ake/24P31A1201_DriveReady_OPC_2026/blob/main/Day-4/Day-04.ipynb)

Comprehensive guide, concepts, and verified implementation details for **Day 4** of the Drive Ready – AI Agents (OPC) Workshop.

---

## 🎯 Task Overview
Upgraded from tool-less chains to **tool-calling AI agents** using LangChain `create_agent`, `@tool` decorators, Pydantic schemas (`Order`), rate-limit/error resilience, and persistent order logging via Google Sheets (`gspread` in Colab) along with a CSV snapshot (`sweet_crumbs_orders.csv`).

- **Primary Notebook:** `Day-04.ipynb`
- **Standalone Script:** `task.py`
- **Domain:** Sweet Crumbs Home Bakery (Menu pricing, store hours, structured order logging, trace inspection & edge-case validation)
- **Regression Test Suite:** `../Day-3/tests.csv` (expanded from 10 to 13 rows)
- **Sheet Output Snapshot:** `sweet_crumbs_orders.csv`
- **Model Used:** `openai/gpt-oss-20b` via Groq (`ChatGroq`, `temperature=0.2`, `max_retries=3`)

---

## 🧠 Core Engineering Concepts

### 1. `@tool` Functions & Why Docstrings Are the Model's API Docs
- Tools expose Python functions to the LLM with typed arguments (`item: str, qty: int = 1`) and clear Google-style docstrings describing when and how to invoke them:
  - `get_price(item: str, qty: int = 1) -> str` — Computes exact rupee totals from `MENU` (`plum cake`: Rs 500, `chocolate cake`: Rs 650, `cupcake`: Rs 80) and returns available items if an off-menu item is requested.
  - `is_open(day: str) -> str` — Checks daily bakery opening hours (`Mon–Sat: 9 am to 8 pm`, `Sun: 10 am to 6 pm`).
  - `log_order(name: str, item: str, qty: int, date: str, eggless: bool) -> str` — Validates incoming orders via Pydantic and appends confirmed rows to Google Sheets.
- **Why Descriptive Names & Docstrings Matter:** The LLM relies on the function name, type hints, and docstring to choose the right tool and pass valid arguments without guessing prices or hours.

### 2. Pydantic Schemas (`Order` Validation)
- **Sweet Crumbs (`Order`):** Validates `name: str`, `item: Literal["plum cake", "chocolate cake", "cupcake"]`, `qty: int` (`ge=1`), `date: str`, and `eggless: bool` before saving any row to Google Sheets.
- Any invalid item name or non-positive quantity (`<= 0`) raises a Pydantic validation error inside `log_order`, returning a clear correction prompt instead of writing bad data to the spreadsheet.

### 3. Reading Agent Traces with `pretty_print()`
For `"Are you open on Sunday? How much are 2 chocolate cakes?"`:
- **Model calls (`AIMessage`):** 3
- **Tool calls requested:** 2 (`['is_open', 'get_price']`)
- **Tool results (`ToolMessage`):** 2

**Execution sequence:**
1. `HumanMessage` → `AIMessage` calls `is_open(day="sunday")` → `ToolMessage` returns `"Open 10 am to 6 pm on sunday."`
2. `AIMessage` calls `get_price(item="chocolate cake", qty=2)` → `ToolMessage` returns `"2 x chocolate cake = Rs 1300"`
3. Final `AIMessage` synthesizes both tool results into a concise, friendly customer reply under 60 words.

### 4. Customer Edge-Case Testing & Sheet Integrity
Tested three adversarial/incomplete customer queries on Sweet Crumbs:
1. **Unlisted item (`"donut"`):** `"Can I order 2 donuts for tomorrow?"` → Explains donuts are not on the menu and lists available items.
2. **Missing pickup date:** `"I'm Sita. Please book 2 plum cakes."` → Asks for the pickup date (and eggless preference) without calling `log_order`.
3. **Invalid quantity (`0` cupcakes):** `"I'm Kiran. Please order 0 cupcakes for 25 Dec."` → Explains minimum quantity is at least 1 (`ge=1`) and asks how many cupcakes are needed.
- **Sheet integrity verified:** Before and after all 3 edge tests, the `Sweet Crumbs Orders` sheet retained only the 1 valid order (`Ravi, chocolate cake, 2, 24 Dec, yes, 1300`).
- **Day 3 `tests.csv` evaluation:** Added these 3 cases as rows 11–13 in `Day-3/tests.csv`.

---

## 🏗️ Implementation Breakdown
1. **Setup & Sheet Connection:** Loads `GROQ_API_KEY` from Colab Secrets (`userdata`) or local `.env`, configures `ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=3)`, and connects to `Sweet Crumbs Orders` via `gspread` (`gc.open_by_url(...)`).
2. **Sweet Crumbs Bakery Agent:** Defines `Order(BaseModel)`, `@tool` functions (`get_price`, `is_open`, `log_order`), and `create_agent(..., system_prompt=SYSTEM)` with multi-turn `history` and `try/except` error resilience.
3. **Trace Inspection:** Prints the full `m.pretty_print()` message trace verifying tool calls, tool responses, and final output.
4. **Edge-Case & Regression Checks:** Verifies off-menu items, missing fields, and `qty < 1` constraints alongside the expanded 13-row `Day-3/tests.csv`.

---

## 📁 Files in `Day-4/`
- `Day-04.ipynb` — Google Colab notebook with Google Sheets setup, Pydantic `Order` schema, `@tool` functions, and `create_agent` execution
- `task.py` — Standalone Python script supporting both Google Colab (`userdata` + `auth`) and local execution
- `sweet_crumbs_orders.csv` — CSV snapshot of confirmed orders logged to Google Sheets
- `.env.example` — Environment variable template (`GROQ_API_KEY`)
- `README.md` — Day 4 documentation

---

## 🚀 How to Run

### In Google Colab
1. Open `Day-4/Day-04.ipynb` via the **Open In Colab** badge above.
2. Add `GROQ_API_KEY` in Colab 🔑 **Secrets** and toggle **Notebook access** to **ON**.
3. Run all cells (`Ctrl + F9`) and complete the Google OAuth prompt when `auth.authenticate_user()` runs to connect `Sweet Crumbs Orders`.

### Locally
1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`.
2. Install dependencies:
   ```bash
   pip install langchain langchain-groq gspread pydantic python-dotenv
