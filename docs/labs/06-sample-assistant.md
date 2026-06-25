---
layout: lab
title: "Lab 6: Sample Assistant"
prev_lab: /labs/05-prompt-engineering
next_lab:
---

# Lab 6: Demo — Build & Deploy a Complete AI Assistant

## 🎯 Learning Objectives

By the end of this lab, you will:
- Build a full-featured AI assistant combining all previous concepts
- Create a web-based chat interface using Streamlit
- Deploy the assistant as an Azure-hosted application
- Have a working end-to-end demo you can showcase

---

## 📑 Table of Contents

| # | Exercise | Type |
|---|----------|------|
| 1 | [What We're Building](#what-were-building) | Concepts |
| 2 | [Portal Step 1: Create the Agent](#portal-step-1-create-the-agent) | 🌐 Portal |
| 3 | [Portal Step 2: Connect Knowledge Base (RAG)](#portal-step-2-connect-your-knowledge-base-rag) | 🌐 Portal |
| 4 | [Portal Step 3: Add Code Interpreter](#portal-step-3-add-code-interpreter-tool) | 🌐 Portal |
| 5 | [Portal Step 4: Test the Assistant](#portal-step-4-test-the-assistant-in-the-playground) | 🌐 Portal |
| 6 | [Portal Step 5: Deploy as Web App (via Code)](#portal-step-5-deploy-as-a-web-app-via-code) | 🐍 CLI |
| 7 | [Portal Step 6: Configure Auth](#portal-step-6-configure-authentication-optional) | 🌐 Portal |
| 8 | [Code Step 1: Create Streamlit Backend](#step-1-create-the-assistant-backend) | 🐍 Code |
| 9 | [Code Step 2: Run Locally](#step-2-run-the-assistant-locally) | 🐍 Code |
| 10 | [Deploy to Azure Container Apps](#option-a-deploy-to-azure-container-apps-recommended) | 🐍 CLI |
| 11 | [Deploy to Azure App Service](#option-b-deploy-to-azure-app-service) | 🐍 CLI |
| 12 | [End-to-End Summary](#-end-to-end-walkthrough-summary) | Reference |
| 13 | [🧪 Final Challenge: Extend the Assistant](#-final-challenge-extend-the-assistant) | Challenge |

---

## What We're Building

A **Customer Support Assistant** for "Contoso Electronics" that:
- ✅ Answers product questions using RAG (grounded in your documents)
- ✅ Uses structured outputs for ticket classification
- ✅ Has conversation memory (multi-turn)
- ✅ Can generate visual diagrams on request
- ✅ Runs as a web application

### Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Streamlit  │────▶│  Python Backend  │────▶│  Azure AI Foundry │
│   Frontend   │◀────│  (FastAPI/Flask) │◀────│  (GPT-4o Agent)   │
└──────────────┘     └────────┬────────┘     └────────┬──────────┘
                              │                        │
                              │                 ┌──────┴──────┐
                              │                 │  Azure AI   │
                              │                 │   Search    │
                              │                 │  (RAG Index)│
                              │                 └─────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Conversation     │
                    │  History (Memory) │
                    └──────────────────┘
```

---

## 🌐 Option A: Build the Assistant via Foundry Portal (No Code)

> You can create a fully functional RAG-powered assistant entirely in the portal — perfect for demos and rapid prototyping.

### Portal Step 1: Create the Agent

1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. Click **Agents** → **+ New agent**
3. Configure:
   - **Name**: `Contoso Support Assistant`
   - **Model**: GPT-4.1
   - **Instructions**:
     ```
     You are the Contoso Electronics AI Assistant. Help customers with product 
     questions, support inquiries, and troubleshooting.
     
     RULES:
     1. Answer based ONLY on the provided knowledge base documents.
     2. If you don't have the answer, suggest contacting support.
     3. Be friendly, professional, and concise.
     4. For support issues, classify priority (low/medium/high/critical).
     5. Always cite your sources.
     ```

### Portal Step 2: Connect Your Knowledge Base (RAG)

1. In the agent configuration, scroll to **Tools**
2. Click **+ Add tool** → **File Search**
3. Click **+ Add data source** → **Azure AI Search**
4. Configure:
   - **Search resource**: Select your Azure AI Search
   - **Index**: Select `hackathon-vector-index` (created in Lab 4)
   - **Search type**: Hybrid (vector + keyword)
   - **Authentication**: Managed Identity or API Key
5. Click **Save**

> 💡 **Alternative — Upload files directly:**
> - Click **+ Add data source** → **Upload files**
> - Drag & drop your sample docs (product-overview.txt, support-policy.txt, troubleshooting-guide.txt)
> - Foundry will automatically chunk, embed, and index them!

### Portal Step 3: Add Code Interpreter Tool

1. Still in the Tools section, click **+ Add tool** → **Code Interpreter**
2. This allows the agent to execute Python for data analysis, chart generation, etc.

### Portal Step 4: Test the Assistant in the Playground

1. Click **Try in playground** (or the chat panel)
2. Test with these questions:
   - *"What products does Contoso offer?"* → Should cite product-overview.txt
   - *"My Contoso Buds won't charge, what should I do?"* → Should cite troubleshooting-guide.txt
   - *"I was charged twice for my order!"* → Should classify as high-priority billing issue
   - *"Create a chart showing product prices"* → Should use Code Interpreter
3. Verify responses cite the correct source documents

### Portal Step 5: Deploy as a Web App (via Code)

> ⚠️ **Note:** The "Deploy to a web app" button is no longer available in the new Foundry portal. Deployment must be done through code using the Azure CLI. The steps below guide you through deploying your agent as a web app.

1. **Get your Agent ID** from the Foundry portal:
   - Go to **Agents** → click your agent → copy the **Agent ID** from the overview panel

2. **Create a minimal web app** that calls your agent. Create a file `app.py`:

   ```python
   import os
   import streamlit as st
   from azure.identity import DefaultAzureCredential
   from azure.ai.projects import AIProjectsClient

   # Configuration
   PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
   AGENT_ID = os.getenv("AGENT_ID")  # The agent you created in the portal

   credential = DefaultAzureCredential()
   client = AIProjectsClient(endpoint=PROJECT_ENDPOINT, credential=credential)

   st.title("🤖 Contoso Electronics Assistant")

   if "thread_id" not in st.session_state:
       thread = client.threads.create(agent_id=AGENT_ID)
       st.session_state.thread_id = thread.id

   # Display chat history
   if "messages" not in st.session_state:
       st.session_state.messages = []

   for msg in st.session_state.messages:
       st.chat_message(msg["role"]).markdown(msg["content"])

   if prompt := st.chat_input("Ask me anything..."):
       st.session_state.messages.append({"role": "user", "content": prompt})
       st.chat_message("user").markdown(prompt)

       # Post message to thread
       client.messages.create(
           thread_id=st.session_state.thread_id, role="user", content=prompt
       )

       # Run the agent
       run = client.runs.create_and_process(thread_id=st.session_state.thread_id)

       if run.status == "completed":
           responses = client.messages.list(thread_id=st.session_state.thread_id)
           for resp in responses:
               if resp.role == "assistant":
                   answer = resp.content[0].text.value
                   st.session_state.messages.append({"role": "assistant", "content": answer})
                   st.chat_message("assistant").markdown(answer)
                   break
   ```

3. **Deploy to Azure Container Apps** using the CLI:

   ```bash
   # Create a resource group
   az group create --name rg-hackathon --location eastus2

   # Create Container Apps environment
   az containerapp env create \
     --name hackathon-env \
     --resource-group rg-hackathon \
     --location eastus2

   # Deploy directly from code (no Dockerfile needed)
   az containerapp up \
     --name contoso-assistant \
     --resource-group rg-hackathon \
     --environment hackathon-env \
     --source . \
     --ingress external \
     --target-port 8501 \
     --env-vars \
       PROJECT_ENDPOINT="<your-project-endpoint>" \
       AGENT_ID="<your-agent-id>"

   # Get the URL
   az containerapp show \
     --name contoso-assistant \
     --resource-group rg-hackathon \
     --query properties.configuration.ingress.fqdn -o tsv
   ```

4. Open the URL — your portal-configured agent is now live as a web app!

### Portal Step 6: Configure Authentication (Optional)

1. In the Azure Portal, go to your Container App → **Authentication**
2. Click **Add identity provider** → select **Microsoft Entra ID**
3. This restricts access to your organization only
4. Or leave it open for the hackathon demo
5. Share the URL with your team to test!

---

## 🐍 Option B: Build the Assistant with Code (Streamlit)

> For full customization and control over the UI and RAG logic.

### Step 1: Create the Assistant Backend

Create `sample-code/05_assistant_app.py`:

```python
"""
Contoso Electronics AI Assistant
A complete RAG-powered assistant with Streamlit UI.
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# ─── Configuration ───────────────────────────────────────────────
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "hackathon-index")

# ─── Initialize Clients ─────────────────────────────────────────
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-12-01-preview"
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# ─── System Prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = """You are the Contoso Electronics AI Assistant. Your role is to help 
customers with product questions, support inquiries, and general information.

RULES:
1. Answer questions based ONLY on the provided context from our knowledge base.
2. If you don't have enough information, say so clearly and suggest contacting support.
3. Be friendly, professional, and concise.
4. For support issues, classify the priority (low/medium/high/critical).
5. If asked to create a diagram, use Mermaid syntax in a code block.

CAPABILITIES:
- Answer product questions (features, pricing, compatibility)
- Explain support policies (warranty, returns, support tiers)
- Classify and route support tickets
- Generate architecture/workflow diagrams
- Provide troubleshooting steps

Always cite your sources when answering from documents."""


# ─── RAG Functions ───────────────────────────────────────────────
def get_embedding(text: str) -> list:
    """Generate embedding for search query."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding


def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """Search the knowledge base using hybrid search."""
    query_embedding = get_embedding(query)
    
    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="content_vector"
    )
    
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["title", "content"],
        top=top_k
    )
    
    context_parts = []
    sources = []
    for result in results:
        context_parts.append(result["content"])
        sources.append(result["title"])
    
    return "\n\n---\n\n".join(context_parts), list(set(sources))


def get_assistant_response(messages: list, use_rag: bool = True) -> tuple:
    """Get response from the assistant with optional RAG."""
    
    # Get the latest user message for RAG search
    user_message = messages[-1]["content"]
    
    context = ""
    sources = []
    
    if use_rag:
        context, sources = search_knowledge_base(user_message)
    
    # Build the full prompt with context
    system_with_context = SYSTEM_PROMPT
    if context:
        system_with_context += f"\n\nRELEVANT CONTEXT FROM KNOWLEDGE BASE:\n{context}"
    
    # Prepare messages for the API
    api_messages = [{"role": "system", "content": system_with_context}]
    api_messages.extend(messages)
    
    # Call the model
    response = openai_client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=api_messages,
        temperature=0.3,
        max_tokens=1000,
        stream=True
    )
    
    return response, sources


# ─── Streamlit UI ────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Contoso Electronics Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Contoso Electronics AI Assistant")
    st.caption("Powered by Azure AI Foundry | RAG-enabled | GPT-4o")
    
    # Sidebar with settings
    with st.sidebar:
        st.header("⚙️ Settings")
        use_rag = st.toggle("Enable RAG (Knowledge Base)", value=True)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3)
        st.divider()
        st.header("📋 Sample Questions")
        st.markdown("""
        Try asking:
        - "What products does Contoso offer?"
        - "What's the return policy?"
        - "I was charged twice, help!"
        - "Create a diagram of the support workflow"
        - "What support tiers are available?"
        """)
        st.divider()
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(f"- {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Contoso Electronics..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get streaming response
            response_stream, sources = get_assistant_response(
                st.session_state.messages, 
                use_rag=use_rag
            )
            
            # Stream the response
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Show sources
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.markdown(f"- {source}")
        
        # Save to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "sources": sources
        })


if __name__ == "__main__":
    main()
```

### Step 2: Run the Assistant Locally

```bash
# Make sure your .env is configured
streamlit run sample-code/05_assistant_app.py
```

The assistant will open in your browser at `http://localhost:8501`.

---

## 🚀 Deploy to Azure

### Option A: Deploy to Azure Container Apps (Recommended)

#### Step 1: Create a Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "sample-code/05_assistant_app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Deploy with Azure CLI

```bash
# Create a resource group (if not exists)
az group create --name rg-hackathon --location eastus2

# Create Azure Container Registry
az acr create --name hackathonfoundry --resource-group rg-hackathon --sku Basic

# Build and push the image
az acr build --registry hackathonfoundry --image contoso-assistant:v1 .

# Create Container Apps environment
az containerapp env create \
  --name hackathon-env \
  --resource-group rg-hackathon \
  --location eastus2

# Deploy the container app
az containerapp create \
  --name contoso-assistant \
  --resource-group rg-hackathon \
  --environment hackathon-env \
  --image hackathonfoundry.azurecr.io/contoso-assistant:v1 \
  --target-port 8501 \
  --ingress external \
  --registry-server hackathonfoundry.azurecr.io \
  --env-vars \
    AZURE_OPENAI_ENDPOINT=<your-endpoint> \
    AZURE_OPENAI_API_KEY=<your-key> \
    AZURE_OPENAI_DEPLOYMENT=gpt-4o \
    AZURE_SEARCH_ENDPOINT=<your-search-endpoint> \
    AZURE_SEARCH_KEY=<your-search-key> \
    AZURE_SEARCH_INDEX=hackathon-index

# Get the URL
az containerapp show \
  --name contoso-assistant \
  --resource-group rg-hackathon \
  --query properties.configuration.ingress.fqdn -o tsv
```

### Option B: Deploy to Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name hackathon-plan \
  --resource-group rg-hackathon \
  --sku B1 --is-linux

# Create web app
az webapp create \
  --name contoso-assistant-app \
  --resource-group rg-hackathon \
  --plan hackathon-plan \
  --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \
  --name contoso-assistant-app \
  --resource-group rg-hackathon \
  --settings \
    AZURE_OPENAI_ENDPOINT=<your-endpoint> \
    AZURE_OPENAI_API_KEY=<your-key> \
    AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Deploy code
az webapp up --name contoso-assistant-app --resource-group rg-hackathon
```

---

## 🎓 End-to-End Walkthrough Summary

Here's what you accomplished across all 6 labs:

```
Lab 1: Foundry Overview
  └── Understood the platform, created a project, deployed a model

Lab 2: Tooling & Setup  
  └── Set up SDK, authenticated, made your first API call

Lab 3: Models & Agents
  └── Used model parameters, built agents with tools, generated diagrams

Lab 4: RAG
  └── Created index, embedded documents, built grounded Q&A

Lab 5: Prompt Engineering
  └── Mastered prompts, structured outputs, JSON schema validation

Lab 6: Sample Assistant (THIS LAB)
  └── Combined everything into a deployed web application! 🎉
```

---

## 🧪 Final Challenge: Extend the Assistant

Choose one or more extensions to implement:

1. **Add File Upload** — Let users upload PDFs that get indexed into the knowledge base
2. **Add Voice Input** — Integrate Azure Speech-to-Text for voice queries
3. **Add Multi-Agent** — Create a routing agent that delegates to specialized sub-agents
4. **Add Evaluation** — Use Foundry's evaluation tools to measure answer quality
5. **Add Safety** — Integrate Azure Content Safety to filter harmful content

---

## ✅ Final Checkpoint

Congratulations! 🎉 You've completed the hackathon. Verify:

- [ ] Your assistant runs locally with Streamlit
- [ ] It answers questions grounded in your documents (RAG)
- [ ] It handles multi-turn conversations
- [ ] It can classify tickets and generate structured output
- [ ] (Bonus) It's deployed to Azure and accessible via URL
- [ ] (Bonus) You've extended it with one of the challenges above

---

## 📚 What's Next?

| Topic | Resource |
|-------|----------|
| Production deployment | [Foundry deployment best practices](https://learn.microsoft.com/en-us/azure/foundry/) |
| Fine-tuning models | [Custom model fine-tuning](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/fine-tuning) |
| Multi-agent systems | [Agent Framework docs](https://learn.microsoft.com/en-us/azure/foundry/agents/) |
| Evaluation & testing | [Foundry evaluation tools](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate/) |
| Content Safety | [Azure AI Content Safety](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/) |

---

**🏆 Thank you for participating in the Azure AI Foundry Hackathon!**

