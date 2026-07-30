"""
01_hello_foundry.py - Your first Azure AI Foundry API call
Lab 2: Tooling & Setup
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

# Make a chat completion call
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Azure AI Foundry? Explain in 3 sentences."}
    ],
    temperature=0.7,
    max_tokens=200
)

print("=" * 60)
print("✅ Hello from Azure AI Foundry!")
print("=" * 60)
print(f"\nResponse:\n{response.choices[0].message.content}")
print(f"\n📊 Token usage:")
print(f"   Prompt tokens:     {response.usage.prompt_tokens}")
print(f"   Completion tokens: {response.usage.completion_tokens}")
print(f"   Total tokens:      {response.usage.total_tokens}")
print(f"\n🏷️  Model: {response.model}")
