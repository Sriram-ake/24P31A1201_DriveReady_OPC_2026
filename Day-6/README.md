# Day 6 — Workflows, Planning & LangGraph (Multi-Agent Router)

**Drive Ready – AI Agents | One Person Company (OPC) Initiative**  
Department of Technical Training, Aditya University

## Overview

Day 6 transitions from a single all-purpose agent (Days 1–5) to **Level 3 Multi-Agent Workflows** using **LangGraph**. Instead of overloading one agent with every tool, a structured workflow classifies customer intent first and routes each message to a focused specialist agent.

## What Was Built

### Part 1 — Sweet Crumbs Home Bakery LangGraph Router
- **Shared State (`TypedDict`):** `BakeryState` tracks `message`, `intent`, and `reply` across nodes.
- **Intent Classifier:** Uses `llm.with_structured_output(Intent)` with `Literal["order", "faq", "other"]` to sort incoming queries deterministically.
- **Conditional Routing & Specialist Agents:**
  - `faq_agent` (`search_faq`, `get_price`, `is_open`) handles policy, pricing, and timing questions without access to `log_order`.
  - `order_agent` (`get_price`, `log_order`) focuses exclusively on validating and recording cake orders.
  - `other` handles greetings and off-topic messages without extra tool calls.
- **Graph Visualization & Streaming:** Verified topology with `draw_mermaid_png()` and traced step-by-step execution via `graph.stream(..., stream_mode="updates")`.

### Part 2 — Your 50%: BrightPage Stationery Multi-Agent Router
- Designed and built a 4-branch LangGraph router (`order`, `print_service`, `faq`, `other`) with dedicated specialist agents (`st_faq_agent`, `st_order_agent`, `st_print_agent`) backed by ChromaDB and pricing tools.

## Files in This Folder

    Day-6/
    ├── .env.example   # Environment variable template for GROQ_API_KEY
    ├── Day-06.ipynb   # Complete Google Colab notebook (Parts 1 & 2 + graph diagrams & stream outputs)
    ├── task.py        # Standalone Python implementation of the Sweet Crumbs LangGraph router
    └── README.md      # Day 6 documentation

## Setup & Run

1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`.
2. Install dependencies:

    pip install langchain langchain-groq langgraph chromadb pydantic python-dotenv

3. Run the standalone router locally:

    python task.py
