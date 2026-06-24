---
layout: lab
title: "Lab 2: Tooling & Setup"
prev_lab: /labs/01-foundry-overview
next_lab: /labs/03-models-and-agents
---

# Lab 2: Tooling & Setup

## 🎯 Learning Objectives

By the end of this lab, you will:
- Have a fully configured development environment
- Understand the SDK ecosystem and when to use each SDK
- Be able to authenticate and make your first API call
- Know how to use the Azure CLI for Foundry operations

---

## SDK Ecosystem Overview

Azure AI Foundry provides multiple SDKs for different scenarios:

| SDK | Package | When to Use |
|-----|---------|-------------|
| **Foundry SDK** | `azure-ai-projects` | General: models, agents, tools, evaluations |
| **OpenAI SDK** | `openai` | Direct OpenAI-compatible calls, lowest latency |
| **Azure Identity** | `azure-identity` | Authentication (Entra ID / Managed Identity) |
| **AI Search SDK** | `azure-search-documents` | Index management, document upload, search |
| **Storage SDK** | `azure-storage-blob` | Document upload to blob storage |

### Language Support
- ✅ Python (primary for this hackathon)
- ✅ C# / .NET
- ✅ JavaScript / TypeScript
- ✅ Java

---

## 🖥️ Hands-On: Environment Setup

### Step 1: Install Required Tools

```bash
# Verify Python version (need 3.11+)
python --version

# Verify Azure CLI
az --version

# Login to Azure
az login

# Set your subscription (if multiple)
az account set --subscription "<your-subscription-id>"
```

### Step 2: Create Project Directory

```bash
mkdir hackathon-foundry && cd hackathon-foundry
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Step 3: Install Python Packages

```bash
pip install azure-ai-projects azure-identity openai python-dotenv
pip install azure-search-documents azure-storage-blob
pip install streamlit pandas
```

### Step 4: Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Fill in your values from the Foundry portal:

```env
# From Azure AI Foundry > Project > Overview
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project

# From Azure OpenAI resource > Keys and Endpoint
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

> 💡 **Where to find these values:**
> - **Project Endpoint**: Foundry Portal → Your Project → Overview → "Project endpoint"
> - **OpenAI Endpoint/Key**: Azure Portal → Your OpenAI resource → Keys and Endpoint
> - **Deployment name**: Foundry Portal → Deployments → Name column

---

## 🖥️ Hands-On: First API Call

### Step 5: Hello Foundry — Using the OpenAI SDK

Create `01_hello_foundry.py`:

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Initialize the client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

# Make a chat completion call
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # Your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Azure AI Foundry? Explain in 2 sentences."}
    ],
    temperature=0.7,
    max_tokens=200
)

print("✅ Response from Azure AI Foundry:")
print(response.choices[0].message.content)
print(f"\n📊 Tokens used: {response.usage.total_tokens}")
```

Run it:
```bash
python 01_hello_foundry.py
```

### Step 6: Using Entra ID Authentication (Recommended for Production)

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

# Use Entra ID — no API keys needed!
credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=credential
)

# List available model deployments
print("📋 Available deployments in your project:")
for deployment in client.deployments.list():
    print(f"  - {deployment.name} ({deployment.model})")
```

---

## 🛠️ Azure CLI for Foundry

Useful CLI commands for managing your Foundry resources:

```bash
# List AI Foundry resources
az cognitiveservices account list --resource-group <rg-name> -o table

# Get endpoint and keys
az cognitiveservices account show --name <resource-name> --resource-group <rg-name>
az cognitiveservices account keys list --name <resource-name> --resource-group <rg-name>

# List model deployments
az cognitiveservices account deployment list \
  --name <resource-name> \
  --resource-group <rg-name> -o table

# Create a model deployment
az cognitiveservices account deployment create \
  --name <resource-name> \
  --resource-group <rg-name> \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

---

## 🔐 Authentication Methods Comparison

| Method | Use Case | Security Level |
|--------|----------|---------------|
| **API Key** | Quick prototyping, hackathons | ⚠️ Low (key rotation needed) |
| **DefaultAzureCredential** | Development (uses az login) | ✅ Medium |
| **Managed Identity** | Production (Azure-hosted apps) | ✅✅ High |
| **Service Principal** | CI/CD pipelines | ✅ Medium-High |

> **Best Practice**: Use `DefaultAzureCredential` during development — it automatically picks up your `az login` session. In production, use Managed Identity.

---

## ✅ Checkpoint

Before moving to the next lab, confirm:
- [ ] Python environment is set up with all packages installed
- [ ] `.env` file is configured with your endpoints and keys
- [ ] You can successfully run `01_hello_foundry.py` and get a response
- [ ] You understand the difference between API key and Entra ID auth

---

**Next:** [Lab 3 — Models & Agents →](03-models-and-agents.md)

