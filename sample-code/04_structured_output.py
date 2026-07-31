"""
04_structured_output.py - Structured Outputs with JSON Schema
Lab 5: Prompt Engineering & Structured Outputs

Uses the Azure OpenAI v1 API (no dated api-version) and Microsoft Entra ID
authentication -- no API keys anywhere in this script. GPT-5.1 is a reasoning
model, so none of these calls use `temperature`.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=f"{endpoint}/openai/v1/", api_key=token_provider)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")


# --- Example 1: Simple JSON Mode ---
def example_json_mode():
    """Basic JSON output using response_format."""
    print("\n" + "=" * 60)
    print("Example 1: Simple JSON Mode")
    print("=" * 60)

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": """Extract the product review into JSON with fields:
            product_name, rating (1-5), pros (array), cons (array), recommendation (boolean)"""},
            {"role": "user", "content": """I bought the Contoso Buds last month and I'm impressed! 
            The noise cancellation is excellent and battery lasts all day. Sound quality is rich 
            and balanced. My only complaints are the case is a bit bulky and they occasionally 
            disconnect during calls. Overall, I'd recommend them. 4 out of 5 stars."""}
        ],
        response_format={"type": "json_object"},  # Forces JSON output
        max_completion_tokens=500,
    )

    result = json.loads(response.choices[0].message.content)
    print(json.dumps(result, indent=2))
    return result


# --- Example 2: Pydantic Schema Validation ---
class SupportTicket(BaseModel):
    ticket_id: str
    category: str  # billing, technical, feature_request, general
    priority: str  # low, medium, high, critical
    sentiment: str  # positive, neutral, negative
    customer_name: Optional[str] = None
    product_mentioned: Optional[str] = None
    summary: str
    suggested_action: str
    requires_escalation: bool


def example_structured_output():
    """Schema-enforced structured output using Pydantic."""
    print("\n" + "=" * 60)
    print("Example 2: Schema-Enforced Structured Output")
    print("=" * 60)

    ticket_text = """Subject: URGENT - Charged 3 times for Contoso Watch Pro!!

    Hi, I'm absolutely furious. I ordered ONE Contoso Watch Pro on June 1st 
    but my credit card shows THREE charges of $349.99. That's over $1000 
    taken from my account! I need this resolved TODAY or I'm disputing with 
    my bank and leaving a review everywhere.
    
    Order #CNT-2026-78432
    - Sarah Mitchell"""

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": """You are a support ticket classifier. 
            Analyze the ticket and extract structured information.
            Use ticket_id from the order number if available, otherwise generate one."""},
            {"role": "user", "content": ticket_text}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "support_ticket",
                "strict": True,
                "schema": SupportTicket.model_json_schema()
            }
        }
    )

    # Guaranteed to match the schema -- Pydantic raises explicitly if it doesn't.
    ticket = SupportTicket.model_validate_json(response.choices[0].message.content)

    print(f"  Ticket ID: {ticket.ticket_id}")
    print(f"  Category: {ticket.category}")
    print(f"  Priority: {ticket.priority}")
    print(f"  Sentiment: {ticket.sentiment}")
    print(f"  Customer: {ticket.customer_name}")
    print(f"  Product: {ticket.product_mentioned}")
    print(f"  Summary: {ticket.summary}")
    print(f"  Action: {ticket.suggested_action}")
    print(f"  Escalate: {ticket.requires_escalation}")
    return ticket


# --- Example 3: Multi-Item Extraction ---
class ProductSpec(BaseModel):
    name: str
    category: str
    price: float
    key_features: List[str]
    warranty_years: int


class ProductCatalog(BaseModel):
    products: List[ProductSpec]
    total_count: int


def example_multi_extraction():
    """Extract multiple structured items from unstructured text."""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Item Extraction")
    print("=" * 60)

    catalog_text = """
    New arrivals this season! The Contoso Hub ($149.99) is our flagship smart home 
    controller with voice activation and 200+ integrations - 2 year warranty. 
    Also check out the Contoso Watch Pro at $349.99 - it's got ECG, SpO2, and 
    5-day battery life with a 2 year warranty. For audio lovers, 
    the Contoso Speaker Max ($199.99) delivers spatial audio with a built-in 
    voice assistant, covered by our standard 2-year warranty.
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Extract all products mentioned with their details."},
            {"role": "user", "content": catalog_text}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "product_catalog",
                "strict": True,
                "schema": ProductCatalog.model_json_schema()
            }
        }
    )

    catalog = ProductCatalog.model_validate_json(response.choices[0].message.content)

    print(f"\n  Found {catalog.total_count} products:\n")
    for p in catalog.products:
        print(f"  {p.name} ({p.category})")
        print(f"     ${p.price:.2f} | {p.warranty_years}yr warranty")
        print(f"     {', '.join(p.key_features[:3])}")
        print()

    return catalog


# --- Main ---
if __name__ == "__main__":
    print("Structured Outputs Demo")
    print("Using Azure AI Foundry with Pydantic schema validation\n")

    example_json_mode()
    example_structured_output()
    example_multi_extraction()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
