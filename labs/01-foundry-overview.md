# Lab 1: Azure AI Foundry Overview

## 🎯 Learning Objectives

By the end of this lab, you will:
- Understand what Azure AI Foundry is and its core components
- Navigate the Foundry portal confidently
- Know the difference between resources, projects, and deployments
- Understand how Foundry fits into the Azure AI ecosystem

---

## What is Azure AI Foundry?

Azure AI Foundry is Microsoft's **unified, enterprise-grade platform** for designing, building, deploying, and governing AI applications and agents at scale.

### Key Value Propositions

| Capability | Description |
|------------|-------------|
| **Model Catalog** | 1,700+ models — OpenAI GPT, Meta Llama, Mistral, Phi, and more |
| **Agent Service** | Build autonomous AI agents with tool calling and multi-step reasoning |
| **RAG Tools** | Built-in retrieval-augmented generation with Azure AI Search |
| **Evaluation** | Test, measure, and improve your AI applications |
| **Governance** | Content safety, responsible AI, access controls |
| **Deployment** | One-click deployment to production endpoints |

---

## Core Concepts

### 1. Resource Hierarchy

```
Azure Subscription
  └── Resource Group
        └── Azure AI Foundry Resource (Hub)
              └── Project
                    ├── Model Deployments
                    ├── Agents
                    ├── Data Connections
                    ├── Indexes
                    └── Evaluations
```

### 2. Projects
A **Project** is your workspace within Foundry. It contains:
- Model deployments (GPT-4o, embeddings, etc.)
- Agents you build
- Connected data sources (Azure AI Search, Storage, etc.)
- Evaluation runs

### 3. Model Deployments
Models from the catalog are deployed as **endpoints** you can call via API:
- **Standard deployments** — pay-per-token, shared infrastructure
- **Provisioned deployments** — dedicated throughput, guaranteed capacity

### 4. Foundry vs. Azure OpenAI Service
| Feature | Azure OpenAI | Azure AI Foundry |
|---------|-------------|-----------------|
| Models | OpenAI only | 1,700+ (OpenAI, Meta, Mistral, etc.) |
| Agents | Assistants API | Full Agent Service |
| RAG | Manual setup | Built-in with AI Search |
| Evaluation | Limited | Comprehensive |
| Governance | Basic | Enterprise-grade |

> **Foundry is the superset** — it includes Azure OpenAI capabilities plus much more.

---

## 🖥️ Hands-On: Portal Walkthrough

### Step 1: Access the Portal
1. Navigate to [https://ai.azure.com](https://ai.azure.com)
2. Sign in with your Azure credentials
3. You'll land on the **Home** page

### Step 2: Explore the Model Catalog
1. Click **Model catalog** in the left navigation
2. Browse available models — filter by:
   - **Task**: Chat, Completion, Embeddings, Image generation
   - **Provider**: OpenAI, Meta, Microsoft, Mistral
   - **License**: Proprietary vs. Open-source
3. Click on **GPT-4o** to see its details, pricing, and benchmarks

### Step 3: Create or Open a Project
1. Click **Projects** in the left nav
2. Click **+ New project**
3. Fill in:
   - **Name**: `hackathon-project`
   - **Hub**: Select your existing Foundry resource (or create new)
   - **Region**: Choose based on model availability
4. Click **Create**

### Step 4: Deploy a Model
1. Inside your project, go to **Deployments**
2. Click **+ Deploy model** → **Deploy base model**
3. Select **GPT-4o** (or GPT-4o-mini for cost savings)
4. Choose deployment type: **Standard**
5. Set tokens-per-minute (TPM) rate limit (start with 10K for hackathon)
6. Click **Deploy**

### Step 5: Test in the Playground
1. Go to **Playgrounds** → **Chat**
2. Select your deployed model
3. Try a prompt:
   ```
   You are a helpful assistant. Explain Azure AI Foundry in 3 sentences.
   ```
4. Experiment with:
   - **System message** (persona/instructions)
   - **Temperature** (creativity: 0 = deterministic, 1 = creative)
   - **Max tokens** (response length limit)

---

## 📊 Key Endpoints You'll Use

After setup, your project provides these endpoints:

| Endpoint Type | URL Pattern | Use Case |
|---------------|-------------|----------|
| Project | `https://<resource>.services.ai.azure.com/api/projects/<project>` | SDK operations |
| OpenAI-compatible | `https://<resource>.openai.azure.com/` | Direct OpenAI SDK calls |
| Model inference | `https://<resource>.services.ai.azure.com/models/<deployment>` | REST API calls |

---

## ✅ Checkpoint

Before moving to the next lab, confirm:
- [ ] You can access the Foundry portal at ai.azure.com
- [ ] You've explored the model catalog
- [ ] You have a project created
- [ ] You've deployed at least one model (GPT-4o or GPT-4o-mini)
- [ ] You've tested the model in the Playground

---

## 📚 Further Reading

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Model Catalog Overview](https://learn.microsoft.com/en-us/azure/foundry/how-to/model-catalog-overview)
- [Foundry Pricing](https://azure.microsoft.com/pricing/details/ai-foundry/)

---

**Next:** [Lab 2 — Tooling & Setup →](02-tooling-setup.md)
