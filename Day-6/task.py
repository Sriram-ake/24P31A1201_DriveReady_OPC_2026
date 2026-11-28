import os
from typing import Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import chromadb
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=3)

# 1. Knowledge Base & Tools
FAQS = {
    "delivery":     "We deliver within 5 km of the bakery. Delivery is Rs 50, free for orders above Rs 1,000.",
    "payment":      "We accept UPI and cash. Orders above Rs 1,000 need a 50% advance by UPI.",
    "cancellation": "Cancellation is free up to 12 hours before pickup. After that, the advance is not refunded.",
    "photo_cake":   "Photo cakes and custom designs need 48 hours' notice.",
    "notice":       "Regular orders need 24 hours' notice.",
    "eggless":      "All our cakes have eggless versions at the same price.",
    "allergens":    "Plum cake contains nuts and dried fruit. Cupcakes and chocolate cake are nut-free.",
    "storage":      "Keep cakes in the fridge and eat them within 3 days.",
    "message":      "A message on the cake is free, up to 20 letters.",
    "candles":      "Candles are free with every cake.",
    "discounts":    "Bulk-order discounts need the owner's approval.",
    "pickup":       "Pickup is during opening hours: Monday to Saturday 9 am to 8 pm, Sunday 10 am to 6 pm.",
}

chroma_client = chromadb.Client()
faq_col = chroma_client.get_or_create_collection(name="sweet_crumbs_day6")
faq_col.upsert(ids=list(FAQS.keys()), documents=list(FAQS.values()))

MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}
HOURS = {
    "monday": "9 am to 8 pm", "tuesday": "9 am to 8 pm", "wednesday": "9 am to 8 pm",
    "thursday": "9 am to 8 pm", "friday": "9 am to 8 pm", "saturday": "9 am to 8 pm",
    "sunday": "10 am to 6 pm"
}
ORDERS_LOG = []

class Order(BaseModel):
    name: str = Field(description="Customer's first name")
    item: Literal["plum cake", "chocolate cake", "cupcake"] = Field(description="Menu item")
    qty: int = Field(description="How many", ge=1)
    date: str = Field(description="Pickup date as the customer said it")
    eggless: bool = Field(description="True if the customer asked for eggless")

@tool
def get_price(item: str, qty: int = 1) -> str:
    """Get the total price in rupees for a quantity of one menu item."""
    price = MENU.get(item.lower().strip())
    if price is None:
        return f"'{item}' is not on the menu. We have: {', '.join(MENU)}."
    return f"{qty} x {item} = Rs {price * qty}"

@tool
def is_open(day: str) -> str:
    """Check the bakery's opening hours for a day of the week, e.g. 'sunday'."""
    hours = HOURS.get(day.lower().strip())
    return f"Open {hours} on {day}." if hours else f"'{day}' is not a day of the week."

@tool
def log_order(name: str, item: str, qty: int, date: str, eggless: bool) -> str:
    """Save a confirmed cake order. Use only when name, item, quantity and pickup date are given."""
    try:
        order = Order(name=name, item=item.lower().strip(), qty=qty, date=date, eggless=eggless)
    except Exception as e:
        return f"Could not save the order: {e}. Ask the customer to correct it."
    total = MENU[order.item] * order.qty
    ORDERS_LOG.append(order.model_dump() | {"total": total})
    return f"Saved: {order.qty} x {order.item} for {order.name} on {order.date}, Rs {total}."

@tool
def search_faq(question: str) -> str:
    """Search Sweet Crumbs' policies and FAQs."""
    results = faq_col.query(query_texts=[question], n_results=3)
    return "\n".join(results["documents"][0])

# 2. LangGraph State & Intent Classifier
class BakeryState(TypedDict):
    message: str
    intent: str
    reply: str

class Intent(BaseModel):
    intent: Literal["order", "faq", "other"] = Field(
        description="order = wants to buy or book cakes; faq = asks about prices, timings, availability or policies; other = greetings or unrelated chat"
    )

classifier = llm.with_structured_output(Intent)

FAQ_PROMPT = """You answer questions for Sweet Crumbs Home Bakery.
Use get_price for prices, is_open for timings and search_faq for policies. Never guess.
If the answer isn't found, say "I'll check with the owner." Under 50 words."""

ORDER_PROMPT = """You take cake orders for Sweet Crumbs Home Bakery.
Use get_price for totals. Before log_order, make sure you have name, item, quantity and
pickup date; ask for anything missing. After saving, read the order back. Under 60 words."""

faq_agent = create_agent(model=llm, tools=[search_faq, get_price, is_open], system_prompt=FAQ_PROMPT)
order_agent = create_agent(model=llm, tools=[get_price, log_order], system_prompt=ORDER_PROMPT)

def classify(state: BakeryState) -> dict:
    return {"intent": classifier.invoke(state["message"]).intent}

def ask_agent(agent, message: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content

def answer_faq(state: BakeryState) -> dict:
    return {"reply": ask_agent(faq_agent, state["message"])}

def take_order(state: BakeryState) -> dict:
    return {"reply": ask_agent(order_agent, state["message"])}

def other(state: BakeryState) -> dict:
    return {"reply": "Hello from Sweet Crumbs! I can help with cakes, prices, orders and our policies."}

def route(state: BakeryState) -> str:
    return state["intent"]

builder = StateGraph(BakeryState)
builder.add_node("classify", classify)
builder.add_node("faq", answer_faq)
builder.add_node("order", take_order)
builder.add_node("other", other)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route, {"order": "order", "faq": "faq", "other": "other"})
builder.add_edge("faq", END)
builder.add_edge("order", END)
builder.add_edge("other", END)

graph = builder.compile()

if __name__ == "__main__":
    tests = [
        "Do you deliver to my area?",
        "I'm Ravi, book 2 eggless plum cakes for 24 Dec",
        "Good morning!",
        "Is the plum cake nut-free?",
    ]
    for msg in tests:
        print("\nCustomer:", msg)
        for step in graph.stream({"message": msg}, stream_mode="updates"):
            print("  ", step)
