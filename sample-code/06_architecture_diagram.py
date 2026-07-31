"""
06_architecture_diagram.py - Generate Architecture Diagrams with AI
Lab 3: Models & Agents - Diagram Generation

Uses the Azure AI Foundry OpenAI v1 endpoint with Microsoft Entra ID
authentication (DefaultAzureCredential) -- no API key is used or required.
GPT-5.1 is a reasoning model and does not support `temperature`.
"""

import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")

if not ENDPOINT:
    sys.exit(
        "ERROR: AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env "
        "and fill in your values (see Lab 2)."
    )

# Microsoft Entra ID authentication -- no API key needed.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)

client = OpenAI(
    base_url=f"{ENDPOINT.rstrip('/')}/openai/v1",
    api_key=token_provider,
)


def generate_mermaid_diagram(description: str) -> str:
    """Generate a Mermaid architecture diagram from a text description."""
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": """You are an expert cloud architect who creates 
            architecture diagrams in Mermaid syntax. 
            
            Rules:
            - Use 'graph TD' for top-down layouts (most common)
            - Use 'graph LR' for left-right layouts (pipeline/flow)
            - Include proper Azure service names
            - Add descriptive labels on connections
            - Use subgraphs to group related components
            - Output ONLY the Mermaid code, no explanation
            """},
            {"role": "user", "content": description}
        ]
    )
    return response.choices[0].message.content


def generate_plantuml_diagram(description: str) -> str:
    """Generate a PlantUML architecture diagram."""
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": """You are an expert cloud architect who creates 
            architecture diagrams in PlantUML syntax.
            
            Rules:
            - Use @startuml and @enduml tags
            - Use proper component diagram notation
            - Include Azure-themed colors (#0078D4 for Azure blue)
            - Label all connections with protocol/purpose
            - Output ONLY the PlantUML code, no explanation
            """},
            {"role": "user", "content": description}
        ]
    )
    return response.choices[0].message.content


# ─── Demo ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🎨 Architecture Diagram Generator")
    print("=" * 60)

    # Example 1: RAG Application Architecture
    print("\n📐 Example 1: RAG Application Architecture (Mermaid)")
    print("-" * 60)

    rag_description = """Create an architecture diagram for a RAG-powered chatbot with:
    - React frontend deployed on Azure Static Web Apps
    - Python FastAPI backend on Azure Container Apps
    - Azure AI Foundry for LLM inference (gpt-5.1)
    - Azure AI Search for vector search
    - Azure Blob Storage for document storage
    - Azure Cosmos DB for conversation history
    - User uploads documents which get processed and indexed"""

    mermaid = generate_mermaid_diagram(rag_description)
    print(mermaid)

    # Save to file
    with open("architecture-rag.mmd", "w") as f:
        f.write(mermaid)
    print("\n✅ Saved to architecture-rag.mmd")

    # Example 2: Microservices Architecture
    print("\n\n📐 Example 2: Microservices Architecture (Mermaid)")
    print("-" * 60)

    microservices_description = """Create a microservices architecture diagram with:
    - Azure API Management as the gateway
    - 4 microservices on Azure Container Apps: Users, Orders, Payments, Notifications
    - Azure Service Bus for async communication between services
    - Azure SQL for Users and Orders databases
    - Azure Cosmos DB for Notifications
    - Azure Key Vault for secrets management
    - Azure Monitor for observability"""

    mermaid2 = generate_mermaid_diagram(microservices_description)
    print(mermaid2)

    with open("architecture-microservices.mmd", "w") as f:
        f.write(mermaid2)
    print("\n✅ Saved to architecture-microservices.mmd")

    # Example 3: PlantUML variant
    print("\n\n📐 Example 3: AI Agent Architecture (PlantUML)")
    print("-" * 60)

    agent_description = """Create a diagram showing an AI Agent architecture with:
    - User interface (web/mobile)
    - Agent orchestrator (Azure AI Foundry Agent Service)
    - Multiple tools: Code Interpreter, Azure AI Search, Custom API
    - Memory store (Azure Cosmos DB)
    - Model endpoint (gpt-5.1)
    - Evaluation & monitoring layer"""

    plantuml = generate_plantuml_diagram(agent_description)
    print(plantuml)

    with open("architecture-agent.puml", "w") as f:
        f.write(plantuml)
    print("\n✅ Saved to architecture-agent.puml")

    print("\n" + "=" * 60)
    print("💡 Tips:")
    print("  - View .mmd files at https://mermaid.live")
    print("  - View .puml files at https://www.plantuml.com/plantuml/uml")
    print("  - VS Code: Install 'Mermaid Preview' extension")
    print("=" * 60)
