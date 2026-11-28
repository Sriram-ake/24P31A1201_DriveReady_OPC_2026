import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import chromadb
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, max_retries=3)

# 1. Knowledge Base (ChromaDB Vector Store)
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
faq_collection = chroma_client.get_or_create_collection(name="sweet_crumbs_faq")
faq_collection.upsert(ids=list(FAQS.keys()), documents=list(FAQS.values()))

# 2. Pricing, Hours & Order Logging
MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}
HOURS = {
    "monday": "9 am to 8 pm",
    "tuesday": "9 am to 8 pm",
    "wednesday": "9 am to 8 pm",
    "thursday": "9 am to 8 pm",
    "friday": "9 am to 8 pm",
    "saturday": "9 am to 8 pm",
    "sunday": "10 am to 6 pm",
}
ORDERS_LOG = []

class Order(BaseModel):
    """A cake order taken from a customer's chat message."""
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
    """Save a confirmed cake order. Use only when name, item, quantity, and pickup date are provided."""
    try:
        order = Order(name=name, item=item.lower().strip(), qty=qty, date=date, eggless=eggless)
    except Exception as e:
        return f"Could not save the order: {e}. Ask the customer to correct it."
    total = MENU[order.item] * order.qty
    ORDERS_LOG.append(order.model_dump() | {"total": total})
    return f"Saved: {order.qty} x {order.item} for {order.name} on {order.date}, Rs {total}."

@tool
def search_faq(question: str) -> str:
    """Search Sweet Crumbs' policies and FAQs: delivery, payment, cancellation,
    photo cakes, allergens, storage, candles, and messages on cakes."""
    results = faq_collection.query(query_texts=[question], n_results=3)
    return "\n".join(results["documents"][0])

SYSTEM = """ROLE:   You are the friendly assistant for Sweet Crumbs Home Bakery.
RULES:  Use get_price for prices and is_open for timings; never guess them.
        For any policy question, use search_faq and answer ONLY from what it returns.
        If the answer isn't there, say "I'll check with the owner."
        Before log_order, make sure you have name, item, quantity and pickup date; ask if missing.
FORMAT: Under 60 words, friendly, English or Telugu matching the customer."""

agent = create_agent(
    model=llm,
    tools=[get_price, is_open, log_order, search_faq],
    system_prompt=SYSTEM,
    checkpointer=InMemorySaver(),
)

def chat(thread_id: str, text: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": text}]}, config)
        return result["messages"][-1].content
    except Exception as e:
        print("Agent error:", e)
        return "Sorry, I'm a little busy. Please try again in a minute."

if __name__ == "__main__":
    print("Ravi 1:", chat("ravi", "Hi, I'm Ravi. Do you deliver? My order is about Rs 1,300."))
    print("Ravi 2:", chat("ravi", "Does the plum cake have nuts?"))
    print("Sravani 1:", chat("sravani", "Can I cancel tomorrow morning if I pick up tomorrow evening?"))
    print("Ravi 3 (Memory + RAG):", chat("ravi", "What's my name, and will I pay for delivery?"))
    print("Sravani 2 (Isolation):", chat("sravani", "What's my name?"))
