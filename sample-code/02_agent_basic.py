"""
02_agent_basic.py - Create a basic AI Agent with Azure AI Foundry
Lab 3: Models & Agents
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

# Initialize with Entra ID authentication
credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=credential
)

print("🤖 Creating AI Agent...")

# Create an agent with instructions
agent = client.agents.create_agent(
    model="gpt-4o",
    name="HackathonHelper",
    instructions="""You are a helpful hackathon assistant for Azure AI Foundry.
    
    Your capabilities:
    - Explain Azure AI concepts clearly
    - Provide Python code examples
    - Help debug common issues
    - Suggest best practices
    
    Keep responses concise and practical. Always include code when relevant."""
)
print(f"✅ Agent created: {agent.id} ({agent.name})")

# Create a conversation thread
thread = client.agents.create_thread()
print(f"✅ Thread created: {thread.id}")

# Have a conversation
questions = [
    "What's the difference between an embedding and a completion model?",
    "Show me a quick example of generating embeddings in Python.",
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"❓ User: {question}")
    print(f"{'='*60}")
    
    # Send message
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=question
    )
    
    # Run the agent
    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    if run.status == "completed":
        messages = client.agents.list_messages(thread_id=thread.id)
        # Get the latest assistant message
        for msg in messages.data:
            if msg.role == "assistant":
                print(f"\n🤖 Assistant:\n{msg.content[0].text.value}")
                break
    else:
        print(f"⚠️ Run status: {run.status}")

# Cleanup
client.agents.delete_agent(agent.id)
print(f"\n🧹 Agent cleaned up.")
