"""
01_hello_foundry.py - Your first Azure AI Foundry API call
Lab 2: Tooling & Setup

Uses the Azure AI Foundry OpenAI v1 endpoint (`{AZURE_OPENAI_ENDPOINT}/openai/v1`)
with Microsoft Entra ID authentication via DefaultAzureCredential -- no API key is
used or required. GPT-5.1 is a reasoning model, so this omits `temperature` and
uses `max_completion_tokens` instead of the older `max_tokens` parameter.
"""

import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")

if not endpoint:
    sys.exit(
        "ERROR: AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env "
        "and fill in your values (see Lab 2)."
    )

# Microsoft Entra ID authentication -- no API key needed.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)

# Plain OpenAI client pointed at the Foundry resource's v1 endpoint.
client = OpenAI(
    base_url=f"{endpoint.rstrip('/')}/openai/v1",
    api_key=token_provider,
)

# Make a chat completion call. GPT-5.1 is a reasoning model: no `temperature`,
# use `max_completion_tokens` (not the deprecated `max_tokens`).
response = client.chat.completions.create(
    model=deployment,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Azure AI Foundry? Explain in 3 sentences."}
    ],
    max_completion_tokens=200
)

print("=" * 60)
print("Hello from Azure AI Foundry!")
print("=" * 60)
print(f"\nResponse:\n{response.choices[0].message.content}")
print(f"\nToken usage:")
print(f"   Prompt tokens:     {response.usage.prompt_tokens}")
print(f"   Completion tokens: {response.usage.completion_tokens}")
print(f"   Total tokens:      {response.usage.total_tokens}")
print(f"\nModel: {response.model}")
