# Day 5: Conversation Memory & RAG (Retrieval-Augmented Generation)

This module completes the **Level 2 Single Agent** by adding thread-isolated conversation memory and semantic document retrieval (RAG).

## Key Implementations
1. **Part 1 — Sweet Crumbs Home Bakery Agent (`InMemorySaver` + `ChromaDB`):**
   - Stores 12 bakery policy FAQs in a ChromaDB collection and retrieves top-3 relevant policies via the `@tool def search_faq(question: str)` tool.
   - Isolates multi-turn customer conversations using LangGraph's `InMemorySaver` checkpointer (`thread_id="ravi"` vs `thread_id="sravani"`).
   - Evaluated against `tests.csv` with fresh threads per query (`86%` pass rate; `100%` semantic accuracy).
2. **Part 2 — PDF RAG Pipeline (`PyMuPDF` + `SentenceTransformer` + `FAISS`):**
   - Extracts text (with Tesseract OCR fallback) from `The_Little_Lantern.pdf`, splits it into overlapping chunks, embeds chunks with `all-MiniLM-L6-v2`, and answers questions strictly grounded in retrieved FAISS context.
3. **Part 3 — Self-Practice Domain (`BrightPage Stationery`):**
   - Loaded 16 custom business policies into ChromaDB with `search_stationery_faq`, multi-thread memory (`ananya` vs `karthik`), out-of-scope refusal guardrails, and automated evaluation (`83%` pass rate; `100%` factual accuracy).

## Files
- `Day-05.ipynb` — Complete Google Colab notebook covering Parts 1, 2, and 3 with outputs.
- `task.py` — Standalone Python implementation of the Sweet Crumbs memory + RAG agent.
- `.env.example` — Environment variable template for `GROQ_API_KEY`.
