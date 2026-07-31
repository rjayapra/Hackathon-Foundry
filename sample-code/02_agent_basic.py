"""
02_agent_basic.py - Create a basic AI Agent with Azure AI Foundry
Lab 3: Models & Agents

Uses the current (non-Classic) Foundry Agent Service surface exposed by
azure-ai-projects >= 2.0 (pinned via requirements.txt in this repo): a named,
versioned "Prompt Agent" is registered with `client.agents.create_version(...)`,
then invoked through the standard OpenAI Responses API by referencing it with
`extra_body={"agent_reference": {...}}`.

Agents terminology note (read this if you've used older Azure AI Foundry samples):
- "Classic Agents" (threads + runs, e.g. `agents.create_agent` /
  `agents.create_thread` / `agents.create_and_process_run`) were the original
  Foundry Agent Service surface, modeled on the now-deprecated OpenAI Assistants
  API. That surface is NOT exposed by azure-ai-projects 2.x (the version pinned
  in this repo) -- treat any sample using those method names as outdated.
- "Prompt Agents" (this sample) are the current, versioned agent resources used
  here: define instructions/model/tools once with `agents.create_version`, then
  call the agent like any other model through the OpenAI Responses API.
"""

import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

AGENT_NAME = "HackathonHelper"
endpoint = os.getenv("PROJECT_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")

if not endpoint:
    sys.exit(
        "ERROR: PROJECT_ENDPOINT is not set. Copy .env.template to .env "
        "and fill in your values (see Lab 2)."
    )

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as client,
):
    print("Creating AI Agent...")

    # Register (or update) a Prompt Agent -- a named, versioned agent resource.
    agent_version = client.agents.create_version(
        AGENT_NAME,
        definition=PromptAgentDefinition(
            model=deployment,
            instructions="""You are a helpful hackathon assistant for Azure AI Foundry.

            Your capabilities:
            - Explain Azure AI concepts clearly
            - Provide Python code examples
            - Help debug common issues
            - Suggest best practices

            Keep responses concise and practical. Always include code when relevant.""",
        ),
    )
    print(f"Agent created: {AGENT_NAME} (version {agent_version.version})")

    questions = [
        "What's the difference between an embedding and a completion model?",
        "Show me a quick example of generating embeddings in Python.",
    ]

    with client.get_openai_client() as openai_client:
        previous_response_id = None
        for question in questions:
            print(f"\n{'=' * 60}")
            print(f"User: {question}")
            print(f"{'=' * 60}")

            response = openai_client.responses.create(
                model=deployment,
                input=question,
                previous_response_id=previous_response_id,
                extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
            )
            previous_response_id = response.id
            print(f"\nAssistant:\n{response.output_text}")

    # Cleanup
    client.agents.delete(AGENT_NAME, force=True)
    print("\nAgent cleaned up.")
