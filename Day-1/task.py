"""Day 1: How LLMs work & First API Call using Groq (OpenAI-compatible & LangChain)."""
import os

try:
    from google.colab import userdata  # type: ignore
    os.environ["GROQ_API_KEY"] = userdata.get("GROQ_API_KEY")
except Exception:
    pass

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-120b"
SYSTEM = """ROLE:   You are the assistant for Sweet Crumbs Home Bakery.
FACTS:  We bake to order. Orders need 24 hours' notice. All cakes have eggless versions.
        Plum cake Rs 500. Chocolate cake Rs 650. Cupcake Rs 80.
RULES:  Never promise a delivery time. If the answer isn't in FACTS, say "I'll check with the owner."
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""


def ask(question: str) -> str:
    """Send a single question with the Sweet Crumbs system prompt."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ],
    )
    print("Token usage:", response.usage)
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print(ask("Can I get an eggless cake today evening?"))
