# Lab 6: Demo — Build & Deploy a Complete AI Assistant

## 🎯 Learning Objectives

By the end of this lab, you will:
- Build a full-featured AI assistant combining all previous concepts
- Create a web-based chat interface using Streamlit
- Deploy the assistant as an Azure-hosted application
- Have a working end-to-end demo you can showcase

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

## 🖥️ Hands-On: Build the Assistant

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
