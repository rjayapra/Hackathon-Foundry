# Azure AI Foundry Hackathon — Hands-On Workshop

## 🎯 Workshop Overview

Welcome to the **Azure AI Foundry Hackathon**! This hands-on workshop takes you from zero to deploying an intelligent AI assistant powered by Azure AI Foundry. By the end, you'll have built a working RAG-powered agent that can answer questions from your own documents.

---

## 📋 Agenda (Full Day — ~6 hours)

| # | Module | Duration | Description |
|---|--------|----------|-------------|
| 1 | [Foundry Overview](labs/01-foundry-overview.md) | 45 min | What is Azure AI Foundry? Platform tour, key concepts |
| 2 | [Tooling & Setup](labs/02-tooling-setup.md) | 45 min | Environment setup, SDKs, CLI, portal walkthrough |
| 3 | [Model Usage & Agents](labs/03-models-and-agents.md) | 75 min | Model catalog, API calls, building agents, architecture diagram generation |
| 4 | [RAG — Retrieval-Augmented Generation](labs/04-rag.md) | 75 min | Azure AI Search, embeddings, indexing, grounded answers |
| 5 | [Prompt Engineering & Structured Outputs](labs/05-prompt-engineering.md) | 60 min | Prompt techniques, JSON mode, schema validation |
| 6 | [Demo: Sample Assistant](labs/06-sample-assistant.md) | 60 min | Build & deploy a complete AI assistant end-to-end |

---

## 🧰 Prerequisites

Before attending the hackathon, ensure you have:

- [ ] **Azure Subscription** with Contributor access
- [ ] **Azure AI Foundry resource** created ([portal](https://ai.azure.com))
- [ ] **Python 3.11+** installed
- [ ] **Azure CLI** installed and logged in (`az login`)
- [ ] **VS Code** with Python and Azure extensions
- [ ] **Git** installed

### Quick Environment Setup

```bash
# Clone this hackathon repo
git clone <your-repo-url>
cd hackathon-foundry

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
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

## 📂 Repository Structure

```
hackathon-foundry/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.template                # Environment variables template
├── labs/
│   ├── 01-foundry-overview.md   # Module 1: Platform overview
│   ├── 02-tooling-setup.md      # Module 2: Tooling & setup
│   ├── 03-models-and-agents.md  # Module 3: Models & agents
│   ├── 04-rag.md                # Module 4: RAG implementation
│   ├── 05-prompt-engineering.md # Module 5: Prompt engineering
│   └── 06-sample-assistant.md   # Module 6: Full demo
├── sample-code/
│   ├── 01_hello_foundry.py      # Basic API call
│   ├── 02_agent_basic.py        # Simple agent creation
│   ├── 03_rag_pipeline.py       # RAG implementation
│   ├── 04_structured_output.py  # Structured output example
│   ├── 05_assistant_app.py      # Complete assistant
│   └── 06_architecture_diagram.py  # Architecture diagram generation
└── data/
    └── sample-docs/             # Sample documents for RAG
```

---

## 🔗 Key Resources

| Resource | Link |
|----------|------|
| Azure AI Foundry Portal | https://ai.azure.com |
| Foundry Documentation | https://learn.microsoft.com/en-us/azure/foundry/ |
| Foundry SDK Reference | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview |
| Agent Service Docs | https://learn.microsoft.com/en-us/azure/foundry/agents/overview |
| Sample Agents Repo | https://github.com/Azure-Samples/ai-foundry-agents-samples |
| Workshop Repo | https://microsoft.github.io/build-your-first-agent-with-azure-ai-agent-service-workshop/ |

---

## 💡 Tips for Hackathon Success

1. **Start with the portal** — explore the UI before writing code
2. **Use GPT-4o** for complex reasoning tasks, **GPT-4o-mini** for cost-effective testing
3. **Test prompts in the playground first** before integrating into code
4. **Keep your .env file secure** — never commit API keys
5. **Ask questions!** — The facilitators are here to help

Good luck and happy hacking! 🚀
