---
layout: default
title: Home
---

# 🚀 Azure AI Foundry Hackathon

Welcome to the **Azure AI Foundry Hackathon**! This hands-on workshop takes you from zero to deploying an intelligent AI assistant powered by Azure AI Foundry.

---

## 📋 Agenda (Full Day — ~6 hours)

| # | Module | Duration | Topic |
|---|--------|----------|-------|
| 1 | [Foundry Overview](labs/01-foundry-overview) | 45 min | Platform tour, key concepts |
| 2 | [Tooling & Setup](labs/02-tooling-setup) | 45 min | SDKs, CLI, portal walkthrough |
| 3 | [Models & Agents](labs/03-models-and-agents) | 75 min | Model catalog, agents, diagram generation |
| 4 | [RAG](labs/04-rag) | 75 min | Azure AI Search, embeddings, grounded answers |
| 5 | [Prompt Engineering](labs/05-prompt-engineering) | 60 min | Prompt techniques, JSON mode, structured outputs |
| 6 | [Sample Assistant](labs/06-sample-assistant) | 60 min | Build & deploy a complete AI assistant |

---

## 🧰 Prerequisites

Before attending, ensure you have:

- ✅ **Azure Subscription** with Contributor access
- ✅ **Azure AI Foundry resource** created at [ai.azure.com](https://ai.azure.com)
- ✅ **Python 3.11+** installed
- ✅ **Azure CLI** installed and logged in (`az login`)
- ✅ **VS Code** with Python and Azure extensions
- ✅ **Git** installed

## ⚡ Quick Start

```bash
# Clone the repo
git clone <your-repo-url>
cd hackathon-foundry

# Set up Python environment
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.template .env
# Edit .env with your Azure endpoints and keys
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Azure AI Foundry                       │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  Model   │   │    Agent     │   │   Evaluation   │  │
│  │ Catalog  │   │   Service    │   │    & Monitor   │  │
│  └────┬─────┘   └──────┬───────┘   └────────────────┘  │
│       │                 │                                │
│  ┌────┴─────────────────┴───────────────────────────┐   │
│  │              Foundry SDK / REST API               │   │
│  └──────────────────────┬───────────────────────────┘   │
│                         │                                │
└─────────────────────────┼────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   ┌──────┴──────┐ ┌─────┴─────┐ ┌──────┴──────┐
   │ Azure AI    │ │  Azure    │ │   Azure     │
   │ Search      │ │  Storage  │ │  Functions  │
   │ (RAG Index) │ │  (Docs)   │ │  (Tools)    │
   └─────────────┘ └───────────┘ └─────────────┘
```

---

## 🔗 Key Resources

| Resource | Link |
|----------|------|
| Azure AI Foundry Portal | [ai.azure.com](https://ai.azure.com) |
| Foundry Documentation | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/foundry/) |
| Foundry SDK Reference | [SDK Overview](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview) |
| Agent Service Docs | [Agents Overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) |
| Sample Agents Repo | [GitHub](https://github.com/Azure-Samples/ai-foundry-agents-samples) |

---

## 💡 Tips

1. **Start with the portal** — explore the UI before writing code
2. **Use GPT-4.1** for complex tasks, **GPT-4.1-mini** for cost-effective testing
3. **Test prompts in the Playground** before integrating into code
4. **Keep your `.env` file secure** — never commit API keys

---

> Ready? Start with **[Lab 1: Foundry Overview →](labs/01-foundry-overview)**
