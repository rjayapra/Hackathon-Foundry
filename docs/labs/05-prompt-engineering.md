---
layout: lab
title: "Lab 5: Prompt Engineering"
prev_lab: /labs/04-rag
next_lab: /labs/06-sample-assistant
---

# Lab 5: Prompt Engineering & Structured Outputs

## 🎯 Learning Objectives

By the end of this lab, you will:
- Master key prompt engineering techniques
- Use system messages effectively to control behavior
- Get reliable structured JSON outputs from models
- Validate model outputs against a schema

---

## 📑 Table of Contents

| # | Exercise | Type |
|---|----------|------|
| 1 | [Prompt Engineering Fundamentals](#prompt-engineering-fundamentals) | Concepts |
| 2 | [Prompt Iteration in the Portal — System Messages](#step-2-practice-system-messages) | 🌐 Portal |
| 3 | [Prompt Iteration in the Portal — Parameters](#step-3-experiment-with-parameters) | 🌐 Portal |
| 4 | [Prompt Iteration in the Portal — JSON Mode](#step-4-test-json-mode-in-the-playground) | 🌐 Portal |
| 5 | [Prompt Iteration in the Portal — Compare Strategies](#step-5-compare-prompt-strategies) | 🌐 Portal |
| 6 | [Prompt Iteration in the Portal — Save Templates](#step-6-save-prompts-as-prompt-templates) | 🌐 Portal |
| 7 | [Technique 1: Role-Based System Messages](#technique-1-role-based-system-messages) | 🐍 Code |
| 8 | [Technique 2: Few-Shot Learning](#technique-2-few-shot-learning) | 🐍 Code |
| 9 | [Technique 3: Chain-of-Thought Prompting](#technique-3-chain-of-thought-prompting) | 🐍 Code |
| 10 | [Structured Outputs — Portal](#-portal-option-structured-outputs-in-the-playground) | 🌐 Portal |
| 11 | [Structured Outputs — JSON Mode (Code)](#method-1-json-mode-simple) | 🐍 Code |
| 12 | [Structured Outputs — JSON Schema (Code)](#method-2-structured-outputs-with-json-schema-production-grade) | 🐍 Code |
| 13 | [Pattern 1: Classification + Extraction](#pattern-1-classification--extraction) | 🐍 Code |
| 14 | [Pattern 2: Multi-Step Processing Pipeline](#pattern-2-multi-step-processing-pipeline) | 🐍 Code |
| 15 | [Best Practices Reference](#-prompt-engineering-best-practices) | Reference |
| 16 | [🧪 Challenge: Document Intelligence Pipeline](#-challenge-exercise) | Challenge |

---

## Prompt Engineering Fundamentals

### The Anatomy of a Good Prompt

```
┌────────────────────────────────────────┐
│ SYSTEM MESSAGE (Persona & Rules)       │
│ "You are a senior cloud architect..."  │
├────────────────────────────────────────┤
│ CONTEXT (Background information)       │
│ "Given this infrastructure setup..."   │
├────────────────────────────────────────┤
│ TASK (Clear instruction)               │
│ "Analyze the setup and identify..."    │
├────────────────────────────────────────┤
│ FORMAT (Output specification)          │
│ "Return as JSON with fields: ..."      │
├────────────────────────────────────────┤
│ EXAMPLES (Few-shot learning)           │
│ "Here's an example: ..."              │
└────────────────────────────────────────┘
```

---

## 🌐 Hands-On: Prompt Engineering in the Foundry Playground (No Code)

> The Foundry Playground is the best place to iterate on prompts before writing code.

### Exercise: Prompt Iteration in the Portal

#### Step 1: Open the Chat Playground
1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. Click **Playgrounds** → **Chat**
3. Select your deployed **GPT-4.1** model

#### Step 2: Practice System Messages
1. In the **System message** box, paste:
   ```
   You are a senior Python code reviewer. Review code for:
   1. Type safety and type hints
   2. Error handling
   3. Documentation (docstrings)
   4. PEP 8 compliance
   
   Rate each category: ✅ Good, ⚠️ Needs improvement, ❌ Missing
   Then provide the improved version.
   ```
2. In the chat, type: `Review this code: def add(a,b): return a+b`
3. Observe the structured, detailed response
4. Now **clear the system message** and ask the same question — notice the difference!

#### Step 3: Experiment with Parameters
1. On the right panel, adjust:
   - **Temperature**: Try `0.0` (deterministic) vs `1.0` (creative) — ask "Write a tagline for an AI hackathon" with each
   - **Max tokens**: Set to `50` and see how responses get truncated
   - **Top-P**: Try `0.1` for very focused output
2. For data extraction tasks, always use **Temperature = 0**

#### Step 4: Test JSON Mode in the Playground
1. In the **System message**, paste:
   ```
   Extract product info from the user's text. Return ONLY a JSON object with fields:
   product_name, brand, price, key_features (array)
   ```
2. Under **Response format** (in the settings panel), select **JSON**
3. Ask: `"The new Surface Pro 10 by Microsoft, Intel Core Ultra 7, 16GB RAM, starts at $1,599"`
4. The response will be guaranteed valid JSON!

#### Step 5: Compare Prompt Strategies
Try these different system messages for the **same user input** and compare results:

| Strategy | System Message |
|----------|---------------|
| **Zero-shot** | `"Extract the person's name, age, and location from the text."` |
| **With format** | `"Extract info as JSON: {name, age, location}"` |
| **With example** | `"Extract info. Example input: 'John, 30, lives in NYC' → {\"name\":\"John\",\"age\":30,\"location\":\"NYC\"}"` |

User input: `"My name is Sarah Chen, I'm 28 years old and I work in Seattle."`

#### Step 6: Save Prompts as Prompt Templates
1. Once you have a prompt you like, click **Save** (top toolbar)
2. Give it a name: `code-reviewer-v1`
3. You can version and share prompts with your team
4. These saved prompts can be accessed via the SDK later

---

## 🐍 Hands-On: Prompt Techniques with Code

### Technique 1: Role-Based System Messages

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

# Bad: No system message
response_bad = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[{"role": "user", "content": "Review this code: def add(a,b): return a+b"}]
)

# Good: Specific role with clear expectations
response_good = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": """You are a senior Python code reviewer. 
        Review code for:
        1. Type safety and type hints
        2. Error handling
        3. Documentation (docstrings)
        4. PEP 8 compliance
        
        Rate each category: ✅ Good, ⚠️ Needs improvement, ❌ Missing
        Then provide the improved version."""},
        {"role": "user", "content": "Review this code: def add(a,b): return a+b"}
    ]
)

print("Without system message:")
print(response_bad.choices[0].message.content[:200])
print("\nWith detailed system message:")
print(response_good.choices[0].message.content)
```

### Technique 2: Few-Shot Learning

```python
# Teach the model your desired format through examples
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extract product info from descriptions."},
        # Example 1
        {"role": "user", "content": "The new MacBook Pro 16\" with M3 Max chip, 36GB RAM, priced at $3,499"},
        {"role": "assistant", "content": '{"product": "MacBook Pro 16\\"", "brand": "Apple", "specs": {"chip": "M3 Max", "ram": "36GB"}, "price": 3499}'},
        # Example 2
        {"role": "user", "content": "Samsung Galaxy S24 Ultra, 12GB RAM, Snapdragon 8 Gen 3, starting at $1,299"},
        {"role": "assistant", "content": '{"product": "Galaxy S24 Ultra", "brand": "Samsung", "specs": {"chip": "Snapdragon 8 Gen 3", "ram": "12GB"}, "price": 1299}'},
        # Actual query
        {"role": "user", "content": "Microsoft Surface Pro 10, Intel Core Ultra 7, 16GB RAM, $1,599 starting price"}
    ],
    temperature=0.0  # Deterministic for structured tasks
)

print(response.choices[0].message.content)
```

### Technique 3: Chain-of-Thought Prompting

```python
# Force the model to reason step-by-step
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": """You are a cloud cost optimizer. 
        When analyzing costs, think step by step:
        1. Identify current resources and their costs
        2. Find optimization opportunities
        3. Calculate potential savings
        4. Provide specific recommendations
        
        Show your reasoning before giving final recommendations."""},
        {"role": "user", "content": """Our Azure bill is $15,000/month:
        - 10 Standard_D4s_v3 VMs running 24/7 ($1,200 each)
        - 5 TB Azure Blob Storage (Hot tier) ($100/TB)
        - Azure SQL Database S3 tier ($450/month)
        - Azure Kubernetes Service with 5 nodes ($800/month)
        How can we reduce costs?"""}
    ]
)

print(response.choices[0].message.content)
```

---

## 📐 Structured Outputs — JSON Mode

### Why Structured Outputs?

When building applications, you need **reliable, parseable** responses — not free-form text.

| Approach | Reliability | When to Use |
|----------|-------------|-------------|
| **Prompt instruction only** | ~80% | Quick prototyping |
| **JSON mode** | ~95% | Most applications |
| **Structured Outputs (schema)** | ~99.9% | Production systems |

---

### 🌐 Portal Option: Structured Outputs in the Playground

> You can test JSON mode and structured outputs directly in the portal before writing code.

#### Test JSON Mode

1. Go to [ai.azure.com](https://ai.azure.com) → your project → **Playgrounds** → **Chat**
2. Select your **GPT-4.1** deployment
3. Set the **System message**:
   ```
   Extract meeting details and return as JSON with fields:
   - title (string)
   - date (ISO 8601)
   - attendees (array of strings)
   - action_items (array of objects with 'task' and 'owner')
   ```
4. In the **Settings** panel (right side), find **Response format** → select **JSON**
5. In chat, type:
   ```
   Meeting notes: The quarterly review was held on March 15, 2026. 
   Attendees: Sarah Chen, Mike Johnson, and Lisa Park. 
   Action items: Sarah will update the roadmap by March 20. 
   Mike needs to review the budget proposal.
   ```
6. The response will be guaranteed valid JSON!

#### Test Ticket Classification

1. Clear the chat and update the **System message**:
   ```
   You are a support ticket classifier. Analyze tickets and return JSON with:
   category (billing/technical/feature_request/general), priority (low/medium/high/critical),
   sentiment (positive/neutral/negative), summary, suggested_action
   ```
2. Keep **Response format** set to **JSON**
3. Paste this ticket:
   ```
   URGENT - I was charged 3 times for my Contoso Watch Pro!! 
   Order #CNT-2026-78432. Fix this TODAY or I'm canceling!
   - Sarah Mitchell
   ```
4. Observe the structured classification output
5. Try different tickets and compare the consistency

#### Compare: JSON vs. No JSON Mode

1. **With JSON mode ON**: The response is always valid JSON — no extra text
2. **Turn JSON mode OFF** (set Response format back to **Text**): The model may include explanations, markdown, or inconsistent formatting
3. This demonstrates why JSON mode matters for production applications

---

### 🐍 Code Option: Structured Outputs

### Method 1: JSON Mode (Simple)

```python
import json

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": """Extract meeting details and return as JSON with these fields:
        - title (string)
        - date (ISO 8601 string)
        - attendees (array of strings)
        - action_items (array of objects with 'task' and 'owner' fields)"""},
        {"role": "user", "content": """Meeting notes: The quarterly review was held on March 15, 2026. 
        Attendees: Sarah Chen, Mike Johnson, and Lisa Park. 
        Action items: Sarah will update the roadmap by March 20. 
        Mike needs to review the budget proposal. 
        Lisa will schedule follow-up meetings with stakeholders."""}
    ],
    response_format={"type": "json_object"},  # ← Forces JSON output
    temperature=0.0
)

# Parse the JSON response
result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))
```

### Method 2: Structured Outputs with JSON Schema (Production-Grade)

```python
from pydantic import BaseModel
from typing import List, Optional

# Define your schema using Pydantic
class ActionItem(BaseModel):
    task: str
    owner: str
    due_date: Optional[str] = None

class MeetingExtraction(BaseModel):
    title: str
    date: str
    attendees: List[str]
    action_items: List[ActionItem]
    summary: str

# Use structured output with schema enforcement
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "Extract meeting information from the provided notes."},
        {"role": "user", "content": """Sprint planning meeting on June 10, 2026.
        Present: Alex Rivera, Jordan Lee, Taylor Smith, Casey Brown.
        Summary: Discussed Q3 priorities. Agreed to focus on AI features.
        Actions: Alex to finalize the API spec by June 15.
        Jordan will set up the CI/CD pipeline by June 12.
        Taylor is researching vector database options, due June 18.
        Casey to present security review findings next meeting."""}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "meeting_extraction",
            "strict": True,
            "schema": MeetingExtraction.model_json_schema()
        }
    }
)

# Guaranteed to match your schema!
meeting = MeetingExtraction.model_validate_json(response.choices[0].message.content)
print(f"📅 Meeting: {meeting.title}")
print(f"📆 Date: {meeting.date}")
print(f"👥 Attendees: {', '.join(meeting.attendees)}")
print(f"\n📋 Action Items:")
for item in meeting.action_items:
    print(f"  • {item.owner}: {item.task} (due: {item.due_date or 'TBD'})")
```

---

## 🖥️ Hands-On: Real-World Structured Output Patterns

### Pattern 1: Classification + Extraction

```python
class TicketAnalysis(BaseModel):
    category: str  # "billing", "technical", "feature_request", "other"
    priority: str  # "low", "medium", "high", "critical"
    sentiment: str  # "positive", "neutral", "negative"
    summary: str
    suggested_response: str

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": """Analyze customer support tickets. 
        Classify, extract key info, and suggest a response.
        Categories: billing, technical, feature_request, other
        Priorities: low, medium, high, critical"""},
        {"role": "user", "content": """Ticket: I've been charged twice for my subscription 
        this month! This is the second time this has happened. I want a refund immediately 
        or I'm canceling my account. Order #12345."""}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "ticket_analysis",
            "strict": True,
            "schema": TicketAnalysis.model_json_schema()
        }
    }
)

ticket = TicketAnalysis.model_validate_json(response.choices[0].message.content)
print(f"Category: {ticket.category}")
print(f"Priority: {ticket.priority}")
print(f"Sentiment: {ticket.sentiment}")
print(f"Summary: {ticket.summary}")
print(f"\nSuggested Response:\n{ticket.suggested_response}")
```

### Pattern 2: Multi-Step Processing Pipeline

```python
from typing import List

class Step(BaseModel):
    step_number: int
    action: str
    azure_service: str
    estimated_time: str
    dependencies: List[str]

class MigrationPlan(BaseModel):
    project_name: str
    source_platform: str
    target_platform: str
    total_estimated_hours: int
    risk_level: str
    steps: List[Step]

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": """You are a cloud migration architect. 
        Create detailed migration plans with specific Azure services and time estimates."""},
        {"role": "user", "content": """Plan migration of a Node.js app from Heroku to Azure. 
        It uses PostgreSQL, Redis, and has a React frontend with file uploads to S3."""}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "migration_plan",
            "strict": True,
            "schema": MigrationPlan.model_json_schema()
        }
    }
)

plan = MigrationPlan.model_validate_json(response.choices[0].message.content)
print(f"🚀 Migration Plan: {plan.project_name}")
print(f"   {plan.source_platform} → {plan.target_platform}")
print(f"   Risk: {plan.risk_level} | Est. Hours: {plan.total_estimated_hours}")
print(f"\n📋 Steps:")
for step in plan.steps:
    print(f"   {step.step_number}. {step.action}")
    print(f"      Service: {step.azure_service} | Time: {step.estimated_time}")
```

---

## 🎯 Prompt Engineering Best Practices

| Principle | Bad Example | Good Example |
|-----------|-------------|--------------|
| **Be specific** | "Summarize this" | "Summarize in 3 bullet points, max 20 words each" |
| **Set boundaries** | "Answer questions" | "Answer ONLY from the provided context" |
| **Define format** | "List the items" | "Return as a numbered list in markdown" |
| **Handle edge cases** | (nothing) | "If unsure, respond with 'I need more info'" |
| **Use temperature** | temp=1.0 for data | temp=0.0 for extraction, 0.7 for creative |

---

## 🧪 Challenge Exercise

**Build a "Document Intelligence" pipeline** that:
1. Takes raw unstructured text (email, report, etc.)
2. Extracts entities (people, dates, amounts, organizations)
3. Classifies the document type
4. Generates a structured summary
5. All outputs in validated JSON schema

---

## ✅ Checkpoint

Before moving to the next lab, confirm:
- [ ] You can write effective system messages with role + rules + format
- [ ] You've used few-shot learning to guide model output format
- [ ] You can enable JSON mode for reliable structured output
- [ ] You've used `json_schema` response format with Pydantic models
- [ ] You understand when to use each approach (prompt-only vs. JSON mode vs. schema)

---

**Next:** [Lab 6 — Demo: Sample Assistant →](06-sample-assistant.md)

