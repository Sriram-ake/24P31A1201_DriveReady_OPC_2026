"""Day 3: Your First AI Agent — LangChain Chain, Memory, tests.csv Evaluation, and create_agent."""

import csv
import os
from pathlib import Path

try:
    from google.colab import userdata  # type: ignore

    os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
except Exception:
    pass

from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

MODEL = "openai/gpt-oss-120b"
MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}

# Prompt v2: clarifies same-day 24-hour notice rule and exact "eggless" wording
SYSTEM = """ROLE:   You are the friendly assistant for Sweet Crumbs Home Bakery.
FACTS:  Plum cake Rs 500. Chocolate cake Rs 650. Cupcake Rs 80 each.
        Orders need 24 hours' notice. All cakes and cupcakes have eggless versions.
RULES:  Never promise a delivery time or place.
        If asked for same-day or today's order, clearly explain that orders need 24 hours' notice.
        Only say "I'll check with the owner." when the question is not covered in FACTS (like delivery areas).
        Always write "eggless" (not "egg-less"). Work out totals carefully.
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""

llm = ChatGroq(model=MODEL, temperature=0.3)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm | StrOutputParser()
history: list[tuple[str, str]] = []


def ask(question: str) -> str:
    """Invoke the LangChain prompt | llm | parser chain with conversation memory."""
    answer = chain.invoke({"history": history, "question": question})
    history.extend([("human", question), ("ai", answer)])
    return answer


DEFAULT_TESTS_PATH = Path(__file__).with_name("tests.csv") if "__file__" in globals() else Path("tests.csv")


def run_tests(path: str | Path = DEFAULT_TESTS_PATH, target_chain=None) -> float:
    """Evaluate all rows in tests.csv and return the pass rate (0.0 to 1.0)."""
    active_chain = target_chain or chain
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    passed = 0
    for row in rows:
        answer = active_chain.invoke({"history": [], "question": row["question"]})
        ok = row["must_include"].lower() in answer.lower()
        passed += int(ok)
        print("PASS" if ok else "FAIL", "|", row["question"], "->", answer[:80])

    rate = passed / len(rows) if rows else 0.0
    print(f"\n{passed}/{len(rows)} passed ({rate:.0%})")
    return rate


# --- Day 4 Prep: Two Python functions with type hints and docstrings ---


def get_price(item: str, qty: int = 1) -> str:
    """Return the total price in rupees for qty of a bakery menu item."""
    key = item.lower().strip()
    if key not in MENU:
        return f"'{item}' is not on our menu. Available items: {', '.join(MENU)}."
    return f"Rs {MENU[key] * qty} for {qty} {key}(s)."


def check_availability(item: str, hours_notice: int = 24) -> str:
    """Check whether an item is on the menu and meets the 24-hour advance notice rule."""
    key = item.lower().strip()
    if key not in MENU:
        return f"'{item}' is not on the menu. I'll check with the owner."
    if hours_notice < 24:
        return f"Orders need at least 24 hours' notice, so {hours_notice} hours is too short."
    return f"Yes, {key} (including eggless) is available with {hours_notice} hours' notice."


if __name__ == "__main__":
    print("--- 1. Memory Test ---")
    print(ask("Hi, I'm Ravi. Do you make eggless cakes?"))
    print(ask("What's my name?"))

    print("\n--- 2. Automated Tests (tests.csv) ---")
    run_tests()

    print("\n--- 3. LangChain create_agent Sneak Peek ---")
    agent = create_agent(model=llm, tools=[], system_prompt=SYSTEM)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Do you make eggless cakes?"}]}
    )
    print(result["messages"][-1].content)
