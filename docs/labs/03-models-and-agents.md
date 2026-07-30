---
layout: lab
title: "Lab 3: Models & Agents"
prev_lab: /labs/02-tooling-setup
next_lab: /labs/04-rag
---

# Lab 3: Model Usage & Agents

## 🎯 Learning Objectives

By the end of this lab, you will:
- Understand the model catalog and how to choose the right model
- Make API calls with different parameters
- Build a basic AI agent with tool calling
- Generate architecture diagrams using AI models

---

## 📑 Table of Contents

| # | Exercise | Type |
|---|----------|------|
| 1 | [Model Catalog Overview](#model-catalog-overview) | Concepts |
| 2 | [Exercise 1: Experiment with Temperature](#exercise-1-experiment-with-temperature) | 🌐 Portal / 🐍 Code |
| 3 | [Exercise 2: Streaming Responses](#exercise-2-streaming-responses) | 🌐 Portal / 🐍 Code |
| 4 | [What is an Agent?](#what-is-an-agent) | Concepts |
| 5 | [Build Your First Agent — Portal](#-option-a-create-an-agent-via-the-foundry-portal-no-code) | 🌐 Portal |
| 6 | [Build Your First Agent — Code](#-option-b-create-an-agent-via-python-sdk) | 🐍 Code |
| 7 | [Exercise 4: Agent with Code Interpreter](#exercise-4-agent-with-code-interpreter-tool) | 🌐 Portal / 🐍 Code |
| 8 | [Architecture Diagram Generation — Portal](#-method-0-generate-diagrams-in-the-foundry-playground-no-code) | 🌐 Portal |
| 9 | [Architecture Diagram Generation — Code](#-method-1-generate-mermaid-diagrams-with-gpt-41) | 🐍 Code |
| 10 | [🧪 Challenge: Architecture Advisor](#-challenge-exercise) | Challenge |

---

## Model Catalog Overview

### Popular Models for Different Tasks (June 2026)

| Model | Best For | Context | Strengths |
|-------|----------|---------|-----------|
| **GPT-4.1** | Complex reasoning, coding, long-context | 1M tokens | SOTA coding & instruction-following, fine-tunable |
| **GPT-4.1-mini** | Cost-effective general tasks | 1M tokens | Fast, affordable, great quality |
| **GPT-4.1-nano** | Ultra-low-latency, edge scenarios | 1M tokens | Smallest/fastest in the 4.1 family |
| **gpt-5.1** | Multimodal (text + image + audio) | 128K tokens | Real-time audio, vision, fastest multimodal |
| **o3** | Advanced math, logic, planning | 200K tokens | Deep chain-of-thought reasoning |
| **o4-mini** | Visual reasoning, cost-efficient reasoning | 200K tokens | Strong reasoning at lower cost |
| **gpt-image-1** | Image generation & editing | — | Text-to-image, inpainting, style transfer |
| **text-embedding-3-large** | Embeddings for RAG | 8K tokens | Best quality embeddings (3072 dimensions) |
| **text-embedding-3-small** | Cost-effective embeddings | 8K tokens | Good quality, lower cost (1536 dimensions) |
| **Phi-4** | On-device/edge AI | 16K tokens | Small, fast, open-source (Microsoft) |

> ⚠️ **Note:** DALL-E 3 was retired in early 2026. Use **gpt-image-1** (or gpt-image-1-mini) for all image generation tasks.

### Choosing a Model — Decision Matrix

```
Need complex reasoning/coding?  → GPT-4.1
Need it cheap & fast?           → GPT-4.1-mini or GPT-4.1-nano
Need multimodal (vision+audio)? → gpt-5.1
Need deep math/logic reasoning? → o3 or o4-mini
Need image generation?          → gpt-image-1
Need embeddings for RAG?        → text-embedding-3-large (quality) or 3-small (cost)
Need code generation?           → GPT-4.1 (1M context, best for code)
Need diagram/visual?            → GPT-4.1 (Mermaid/PlantUML) + gpt-image-1
Need long documents (>128K)?    → GPT-4.1 (1M token context)
```

---

## 🖥️ Hands-On: API Parameters Deep Dive

### Exercise 1: Experiment with Temperature

#### 🌐 Portal Option

1. Go to [ai.azure.com](https://ai.azure.com) → your project → **Playgrounds** → **Chat**
2. Select your **GPT-4.1** deployment
3. In the chat, type: *"Write a one-line tagline for an AI hackathon."*
4. On the right panel, set **Temperature** to `0.0` → press Send
5. **Clear chat**, ask the same question with Temperature `0.5` → Send
6. **Clear chat**, ask the same question with Temperature `1.0` → Send
7. Compare the three responses — notice how higher temperature = more creative/varied output

> 💡 **Key insight**: Temperature `0.0` gives the same answer every time. Temperature `1.0` is different each time.

#### 🐍 Code Option

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-04-01-preview"
)

prompt = "Write a one-line tagline for an AI hackathon."

# Try different temperatures
for temp in [0.0, 0.5, 1.0]:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        max_tokens=50
    )
    print(f"Temperature {temp}: {response.choices[0].message.content}")
```

### Exercise 2: Streaming Responses

#### 🌐 Portal Option

1. In the **Chat Playground**, the Foundry portal streams responses by default!
2. Ask a longer question: *"Explain microservices architecture in 5 bullet points."*
3. Watch the tokens appear one by one — this is streaming in action
4. In a real application, streaming gives users faster perceived response times
5. Toggle **Stream response** in the settings panel to compare streaming vs. non-streaming

> 💡 **Key insight**: Streaming shows partial results immediately. Without streaming, users wait for the full response.

#### 🐍 Code Option

```python
# Streaming — get tokens as they're generated (great for chat UIs)
stream = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain microservices architecture in 5 bullet points."}
    ],
    stream=True
)

print("Streaming response:")
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

---

## 🤖 Building AI Agents

### What is an Agent?

An **AI Agent** is an autonomous system that can:
1. **Understand** user intent from natural language
2. **Plan** multi-step actions to accomplish goals
3. **Use tools** (search, code execution, APIs) to gather information
4. **Respond** with grounded, actionable answers

### Agent Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│   Agent Brain   │ ← LLM (gpt-5.1)
│  (Reasoning)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Tools  │
    ├─────────┤
    │ • Code Interpreter    │
    │ • File Search (RAG)   │
    │ • Function Calling    │
    │ • Azure AI Search     │
    │ • Custom APIs         │
    └─────────────────────────┘
         │
         ▼
   Grounded Response
```

---

## 🖥️ Hands-On: Building Your First Agent

### 🌐 Option A: Create an Agent via the Foundry Portal (No Code)

> This approach is ideal for quickly prototyping and testing agents without writing code.

#### Step 1: Open the Agent Builder
1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. Click **Agents** in the left navigation
3. Click **+ New agent**

#### Step 2: Configure the Agent
1. **Name**: `HackathonHelper`
2. **Model**: Select your deployed GPT-4.1 (or GPT-4.1-mini)
3. **Instructions** (paste into the System message box):
   ```
   You are a helpful hackathon assistant for Azure AI Foundry.
   Your capabilities:
   - Explain Azure AI concepts clearly
   - Provide Python code examples
   - Help debug common issues
   - Suggest best practices
   Keep responses concise and practical. Always include code when relevant.
   ```

#### Step 3: Add Tools
1. In the **Tools** section, click **+ Add tool**
2. Select **Code Interpreter** — enables the agent to execute Python code
3. (Optional) Select **File Search** — enables RAG over uploaded files

#### Step 4: Test the Agent
1. Click **Try in playground** (or the chat panel on the right)
2. Ask: *"What's the difference between an embedding and a completion model?"*
3. Observe the agent reasoning and responding
4. Try: *"Write Python code to generate embeddings using Azure OpenAI"* — the agent will use Code Interpreter

#### Step 5: Upload Files for File Search (Optional)
1. In the agent config, under **File Search**, click **+ Add data source**
2. Upload the sample documents from `data/sample-docs/`
3. The agent will now answer questions grounded in your documents

#### Step 6: Save & Deploy
1. Click **Save** to save your agent configuration
2. Note the **Agent ID** — you'll use this if calling from code later
3. You can share the agent with teammates via the portal

---

### 🐍 Option B: Create an Agent via Python SDK

### Exercise 3: Basic Agent with Azure AI Foundry

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Agent, AgentThread, ThreadMessage, ThreadRun

load_dotenv()

# Initialize client
credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=credential
)

# Step 1: Create an Agent
agent = client.agents.create_agent(
    model="gpt-5.1",
    name="HackathonHelper",
    instructions="""You are a helpful hackathon assistant. You help developers 
    understand Azure AI services and write code. Be concise and practical.
    Always provide code examples when relevant."""
)
print(f"✅ Agent created: {agent.id}")

# Step 2: Create a conversation thread
thread = client.agents.create_thread()
print(f"✅ Thread created: {thread.id}")

# Step 3: Send a message
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="How do I create a RAG pipeline with Azure AI Search? Give me the key steps."
)

# Step 4: Run the agent
run = client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id
)

# Step 5: Get the response
if run.status == "completed":
    messages = client.agents.list_messages(thread_id=thread.id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print(f"\n🤖 Agent Response:\n{msg.content[0].text.value}")

# Cleanup
client.agents.delete_agent(agent.id)
print("\n🧹 Agent cleaned up.")
```

### Exercise 4: Agent with Code Interpreter Tool

#### 🌐 Portal Option

1. In the Foundry portal, go to **Agents** → open the agent you created in Option A (or create a new one)
2. Ensure **Code Interpreter** is enabled in the Tools section
3. In the agent chat, ask:
   ```
   Create a bar chart showing these quarterly sales:
   Q1: $45,000  Q2: $52,000  Q3: $48,000  Q4: $61,000
   Save it as a PNG file.
   ```
4. The agent will write and execute Python code, then display the chart inline!
5. You can download the generated PNG from the chat

> 💡 The agent can also analyze uploaded files. Try uploading a CSV and asking it to summarize the data.

#### 🐍 Code Option

```python
# Create an agent that can execute Python code
agent = client.agents.create_agent(
    model="gpt-5.1",
    name="DataAnalyst",
    instructions="You are a data analyst. Use code interpreter to analyze data and create visualizations.",
    tools=[{"type": "code_interpreter"}]
)

# Ask it to do data analysis
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="""Create a bar chart showing these quarterly sales:
    Q1: $45,000
    Q2: $52,000  
    Q3: $48,000
    Q4: $61,000
    Save it as a PNG file."""
)

run = client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id
)

# The agent will execute Python code to create the chart
```

---

## 🎨 Architecture Diagram Generation

AI models can generate architecture diagrams in multiple ways:

### 🌐 Method 0: Generate Diagrams with an Agent (Portal)

> Create a dedicated Architecture Diagram agent in the Foundry portal.

#### Step 1: Create the Diagram Agent
1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. Click **Agents** → **+ New agent**
3. Configure:
   - **Name**: `ArchitectureDiagramGenerator`
   - **Model**: Select your deployed **GPT-4.1**
   - **Instructions**:
     ```
     You are an expert cloud architect specializing in Azure. When asked to 
     create architecture diagrams:
     
     1. ALWAYS output diagrams in Mermaid syntax inside a ```mermaid code block
     2. Use 'graph TD' for top-down layouts or 'graph LR' for left-right flows
     3. Use subgraphs to group related Azure services
     4. Add descriptive labels on all connections (e.g., "HTTPS", "REST API")
     5. Include proper Azure service names
     6. After the diagram, provide a brief explanation of the data flow
     
     If asked to generate an image diagram, use Code Interpreter with matplotlib.
     ```

#### Step 2: Add Code Interpreter Tool
1. In the **Tools** section, click **+ Add tool** → **Code Interpreter**
2. This allows the agent to also generate PNG/SVG diagrams using matplotlib

#### Step 3: Test the Agent
1. In the agent chat panel, ask:
   ```
   Create an architecture diagram for a RAG-powered chatbot with:
   - React frontend on Azure Static Web Apps
   - Python API on Azure Container Apps
   - Azure AI Foundry for LLM inference
   - Azure AI Search for vector search
   - Azure Blob Storage for documents
   - Azure Cosmos DB for chat history
   ```
2. The agent will output a Mermaid diagram — copy the code
3. Paste it into [mermaid.live](https://mermaid.live) to see the visual diagram
4. Export as PNG/SVG for your presentations

#### Step 4: Try Image Generation
1. Ask the same agent:
   ```
   Now create a visual PNG diagram of this same architecture using matplotlib. 
   Use boxes and arrows with Azure blue colors (#0078D4). Save as PNG.
   ```
2. The agent will use Code Interpreter to generate and display the image
3. Download the PNG directly from the chat

> 💡 **Pro tip:** Install the **Mermaid Preview** extension in VS Code to render `.mmd` files directly in your editor.

### 🐍 Method 1: Generate Mermaid Diagrams with GPT-4.1

```python
response = client.chat.completions.create(
    model="gpt-4.1",  # Best for code/structured output generation
    messages=[
        {"role": "system", "content": """You are an expert cloud architect. 
        When asked to create architecture diagrams, output them in Mermaid syntax.
        Use proper Mermaid graph notation with clear labels."""},
        {"role": "user", "content": """Create an architecture diagram for a 
        web application with:
        - React frontend on Azure Static Web Apps
        - Python API on Azure Container Apps
        - Azure SQL Database
        - Azure AI Foundry for AI features
        - Azure AI Search for RAG
        - Azure Blob Storage for documents"""}
    ],
    temperature=0.3
)

mermaid_code = response.choices[0].message.content
print(mermaid_code)

# Save to file — render with any Mermaid viewer (VS Code extension, mermaid.live)
with open("architecture.mmd", "w") as f:
    f.write(mermaid_code)
```

**Example output:**
```mermaid
graph TD
    A[React Frontend] -->|HTTPS| B[Azure Static Web Apps]
    B -->|API Calls| C[Azure Container Apps - Python API]
    C -->|Query| D[Azure SQL Database]
    C -->|AI Inference| E[Azure AI Foundry]
    C -->|Search| F[Azure AI Search]
    F -->|Index| G[Azure Blob Storage]
    E -->|RAG| F
```

### Method 2: Generate Images with gpt-image-1

```python
# Use gpt-image-1 for visual architecture diagrams
response = client.images.generate(
    model="gpt-image-1",
    prompt="""Create a clean, professional cloud architecture diagram showing:
    - A web browser connecting to Azure App Service
    - App Service connecting to Azure AI Foundry
    - Azure AI Foundry connecting to Azure AI Search
    - Azure AI Search connecting to Azure Blob Storage
    Use a modern flat design style with Azure blue colors.
    Include Azure service icons. White background.""",
    size="1024x1024",
    quality="high",
    n=1
)

image_url = response.data[0].url
print(f"🎨 Diagram generated: {image_url}")
```

### Method 3: Generate PlantUML with Code Interpreter

```python
# Use the agent with code interpreter to generate diagrams
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="""Generate a PlantUML diagram for a microservices architecture with:
    - API Gateway
    - User Service
    - Order Service  
    - Payment Service
    - Message Queue between services
    Output the PlantUML code and also render it as a PNG using the plantuml library."""
)
```

---

## 🧪 Challenge Exercise

**Build a "Architecture Advisor" agent** that:
1. Takes a text description of an application
2. Recommends Azure services to use
3. Generates a Mermaid architecture diagram
4. Explains the data flow

```python
# Starter code for the challenge
advisor_agent = client.agents.create_agent(
    model="gpt-5.1",
    name="ArchitectureAdvisor",
    instructions="""You are an Azure Solutions Architect. When given an application 
    description:
    1. Recommend the best Azure services
    2. Generate a Mermaid diagram showing the architecture
    3. Explain the data flow between components
    4. Note any scalability or security considerations
    
    Always output the Mermaid diagram in a code block with ```mermaid markers.""",
    tools=[{"type": "code_interpreter"}]
)
```

---

## ✅ Checkpoint

Before moving to the next lab, confirm:
- [ ] You can make API calls with different parameters (temperature, streaming)
- [ ] You've created and interacted with an agent
- [ ] You understand tool calling (code interpreter)
- [ ] You can generate architecture diagrams using GPT-4.1 (Mermaid)
- [ ] (Bonus) You've completed the Architecture Advisor challenge

---

**Next:** [Lab 4 — RAG (Retrieval-Augmented Generation) →](04-rag.md)

