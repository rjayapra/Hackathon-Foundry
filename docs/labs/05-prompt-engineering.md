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

## 🐍 / .NET Hands-On: Prompt Techniques with Code

### Technique 1: Role-Based System Messages

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=f"{endpoint}/openai/v1/", api_key=token_provider)

# Bad: No system message
response_bad = client.chat.completions.create(
    model=deployment,
    messages=[{"role": "user", "content": "Review this code: def add(a,b): return a+b"}],
    max_completion_tokens=300,
)

# Good: Specific role with clear expectations
response_good = client.chat.completions.create(
    model=deployment,
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
    ],
    max_completion_tokens=600,
)

print("Without system message:")
print(response_bad.choices[0].message.content[:200])
print("\nWith detailed system message:")
print(response_good.choices[0].message.content)
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

// BearerTokenPolicy-based authentication is currently marked [Experimental("OPENAI001")]
// in the OpenAI .NET SDK. All the usings above are shared by every example below --
// they must stay together at the top of Program.cs.
#pragma warning disable OPENAI001

string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
string deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5.1";

BearerTokenPolicy tokenPolicy = new(new DefaultAzureCredential(), "https://ai.azure.com/.default");
ChatClient client = new(
    model: deployment,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions { Endpoint = new Uri($"{endpoint.TrimEnd('/')}/openai/v1/") });

// Bad: no system message
ChatCompletion badCompletion = client.CompleteChat(
    [new UserChatMessage("Review this code: def add(a,b): return a+b")],
    new ChatCompletionOptions { MaxOutputTokenCount = 300 });

// Good: specific role with clear expectations
const string ReviewerInstructions = """
    You are a senior Python code reviewer.
    Review code for:
    1. Type safety and type hints
    2. Error handling
    3. Documentation (docstrings)
    4. PEP 8 compliance

    Rate each category: Good, Needs improvement, Missing
    Then provide the improved version.
    """;

ChatCompletion goodCompletion = client.CompleteChat(
    [
        new SystemChatMessage(ReviewerInstructions),
        new UserChatMessage("Review this code: def add(a,b): return a+b"),
    ],
    new ChatCompletionOptions { MaxOutputTokenCount = 600 });

Console.WriteLine("Without system message:");
string badText = badCompletion.Content[0].Text;
Console.WriteLine(badText[..Math.Min(200, badText.Length)]);
Console.WriteLine("\nWith detailed system message:");
Console.WriteLine(goodCompletion.Content[0].Text);
```

</div>
</div>

### Technique 2: Few-Shot Learning

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
# Teach the model your desired format through examples
response = client.chat.completions.create(
    model=deployment,
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
    max_completion_tokens=300,  # Few-shot examples make the format consistent -- no temperature needed
)

print(response.choices[0].message.content)
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
// Teach the model your desired format through examples
ChatCompletion fewShotCompletion = client.CompleteChat(
    [
        new SystemChatMessage("Extract product info from descriptions."),
        // Example 1
        new UserChatMessage("The new MacBook Pro 16\" with M3 Max chip, 36GB RAM, priced at $3,499"),
        new AssistantChatMessage("""{"product": "MacBook Pro 16\"", "brand": "Apple", "specs": {"chip": "M3 Max", "ram": "36GB"}, "price": 3499}"""),
        // Example 2
        new UserChatMessage("Samsung Galaxy S24 Ultra, 12GB RAM, Snapdragon 8 Gen 3, starting at $1,299"),
        new AssistantChatMessage("""{"product": "Galaxy S24 Ultra", "brand": "Samsung", "specs": {"chip": "Snapdragon 8 Gen 3", "ram": "12GB"}, "price": 1299}"""),
        // Actual query
        new UserChatMessage("Microsoft Surface Pro 10, Intel Core Ultra 7, 16GB RAM, $1,599 starting price"),
    ],
    new ChatCompletionOptions { MaxOutputTokenCount = 300 });

Console.WriteLine(fewShotCompletion.Content[0].Text);
```

</div>
</div>

### Technique 3: Chain-of-Thought Prompting (Reasoning Guidance)

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
# Force the model to reason step-by-step
response = client.chat.completions.create(
    model=deployment,
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
    ],
    reasoning_effort="high",  # Raise reasoning effort for multi-step analysis
    max_completion_tokens=1200,
)

print(response.choices[0].message.content)
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
// Force the model to reason step-by-step
const string CostOptimizerInstructions = """
    You are a cloud cost optimizer.
    When analyzing costs, think step by step:
    1. Identify current resources and their costs
    2. Find optimization opportunities
    3. Calculate potential savings
    4. Provide specific recommendations

    Show your reasoning before giving final recommendations.
    """;

const string CostQuestion = """
    Our Azure bill is $15,000/month:
    - 10 Standard_D4s_v3 VMs running 24/7 ($1,200 each)
    - 5 TB Azure Blob Storage (Hot tier) ($100/TB)
    - Azure SQL Database S3 tier ($450/month)
    - Azure Kubernetes Service with 5 nodes ($800/month)
    How can we reduce costs?
    """;

ChatCompletion reasoningCompletion = client.CompleteChat(
    [
        new SystemChatMessage(CostOptimizerInstructions),
        new UserChatMessage(CostQuestion),
    ],
    new ChatCompletionOptions
    {
        ReasoningEffortLevel = ChatReasoningEffortLevel.High,  // Raise effort for multi-step analysis
        MaxOutputTokenCount = 1200,
    });

Console.WriteLine(reasoningCompletion.Content[0].Text);
```

</div>
</div>

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

### 🐍 / .NET Code Option: Structured Outputs

### Method 1: JSON Mode (Simple)

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
import json

response = client.chat.completions.create(
    model=deployment,
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
    max_completion_tokens=500,
)

# Parse the JSON response
result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
const string MeetingSystemPrompt = """
    Extract meeting details and return as JSON with these fields:
    - title (string)
    - date (ISO 8601 string)
    - attendees (array of strings)
    - action_items (array of objects with 'task' and 'owner' fields)
    """;
const string MeetingNotes = """
    Meeting notes: The quarterly review was held on March 15, 2026. Attendees:
    Sarah Chen, Mike Johnson, and Lisa Park. Action items: Sarah will update the
    roadmap by March 20. Mike needs to review the budget proposal. Lisa will
    schedule follow-up meetings with stakeholders.
    """;

ChatCompletionOptions jsonModeOptions = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonObjectFormat(),  // Forces JSON output
    MaxOutputTokenCount = 500,
};

ChatCompletion jsonModeCompletion = client.CompleteChat(
    [
        new SystemChatMessage(MeetingSystemPrompt),
        new UserChatMessage(MeetingNotes),
    ],
    jsonModeOptions);

// Parse the JSON response
using JsonDocument meetingJson = JsonDocument.Parse(jsonModeCompletion.Content[0].Text);
Console.WriteLine(JsonSerializer.Serialize(meetingJson.RootElement, new JsonSerializerOptions { WriteIndented = true }));
```

</div>
</div>

### Method 2: Structured Outputs with JSON Schema (Production-Grade)

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

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
    model=deployment,
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

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
// Define your schema as records -- the .NET equivalent of the Pydantic models
record ActionItem(
    [property: JsonPropertyName("task")] string Task,
    [property: JsonPropertyName("owner")] string Owner,
    [property: JsonPropertyName("due_date")] string? DueDate);

record MeetingExtraction(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("date")] string Date,
    [property: JsonPropertyName("attendees")] List<string> Attendees,
    [property: JsonPropertyName("action_items")] List<ActionItem> ActionItems,
    [property: JsonPropertyName("summary")] string Summary);

const string MeetingSchemaJson = """
    {
        "type": "object",
        "properties": {
            "title": { "type": "string" },
            "date": { "type": "string" },
            "attendees": { "type": "array", "items": { "type": "string" } },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": { "type": "string" },
                        "owner": { "type": "string" },
                        "due_date": { "type": ["string", "null"] }
                    },
                    "required": ["task", "owner", "due_date"],
                    "additionalProperties": false
                }
            },
            "summary": { "type": "string" }
        },
        "required": ["title", "date", "attendees", "action_items", "summary"],
        "additionalProperties": false
    }
    """;

// Use structured output with schema enforcement
ChatCompletionOptions schemaOptions = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
        jsonSchemaFormatName: "meeting_extraction",
        jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(MeetingSchemaJson)),
        jsonSchemaIsStrict: true),
};

ChatCompletion schemaCompletion = client.CompleteChat(
    [
        new SystemChatMessage("Extract meeting information from the provided notes."),
        new UserChatMessage("""
            Sprint planning meeting on June 10, 2026. Present: Alex Rivera, Jordan
            Lee, Taylor Smith, Casey Brown. Summary: Discussed Q3 priorities.
            Agreed to focus on AI features. Actions: Alex to finalize the API spec
            by June 15. Jordan will set up the CI/CD pipeline by June 12. Taylor is
            researching vector database options, due June 18. Casey to present
            security review findings next meeting.
            """),
    ],
    schemaOptions);

// Guaranteed to match your schema! Fail explicitly rather than continuing with null.
MeetingExtraction meeting = JsonSerializer.Deserialize<MeetingExtraction>(schemaCompletion.Content[0].Text)
    ?? throw new InvalidOperationException("Model returned an empty structured response.");

Console.WriteLine($"Meeting: {meeting.Title}");
Console.WriteLine($"Date: {meeting.Date}");
Console.WriteLine($"Attendees: {string.Join(", ", meeting.Attendees)}");
Console.WriteLine("\nAction Items:");
foreach (ActionItem item in meeting.ActionItems)
{
    Console.WriteLine($"  {item.Owner}: {item.Task} (due: {item.DueDate ?? "TBD"})");
}
```

</div>
</div>

---

## 🖥️ Hands-On: Real-World Structured Output Patterns

### Pattern 1: Classification + Extraction

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
class TicketAnalysis(BaseModel):
    category: str  # "billing", "technical", "feature_request", "other"
    priority: str  # "low", "medium", "high", "critical"
    sentiment: str  # "positive", "neutral", "negative"
    summary: str
    suggested_response: str

response = client.chat.completions.create(
    model=deployment,
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

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
record TicketAnalysis(
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("priority")] string Priority,
    [property: JsonPropertyName("sentiment")] string Sentiment,
    [property: JsonPropertyName("summary")] string Summary,
    [property: JsonPropertyName("suggested_response")] string SuggestedResponse);

const string TicketSchemaJson = """
    {
        "type": "object",
        "properties": {
            "category": { "type": "string" },
            "priority": { "type": "string" },
            "sentiment": { "type": "string" },
            "summary": { "type": "string" },
            "suggested_response": { "type": "string" }
        },
        "required": ["category", "priority", "sentiment", "summary", "suggested_response"],
        "additionalProperties": false
    }
    """;

ChatCompletionOptions ticketOptions = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
        jsonSchemaFormatName: "ticket_analysis",
        jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(TicketSchemaJson)),
        jsonSchemaIsStrict: true),
};

ChatCompletion ticketCompletion = client.CompleteChat(
    [
        new SystemChatMessage("""
            Analyze customer support tickets. Classify, extract key info, and
            suggest a response. Categories: billing, technical, feature_request,
            other. Priorities: low, medium, high, critical
            """),
        new UserChatMessage("""
            Ticket: I've been charged twice for my subscription this month! This is
            the second time this has happened. I want a refund immediately or I'm
            canceling my account. Order #12345.
            """),
    ],
    ticketOptions);

TicketAnalysis ticket = JsonSerializer.Deserialize<TicketAnalysis>(ticketCompletion.Content[0].Text)
    ?? throw new InvalidOperationException("Model returned an empty structured response.");

Console.WriteLine($"Category: {ticket.Category}");
Console.WriteLine($"Priority: {ticket.Priority}");
Console.WriteLine($"Sentiment: {ticket.Sentiment}");
Console.WriteLine($"Summary: {ticket.Summary}");
Console.WriteLine($"\nSuggested Response:\n{ticket.SuggestedResponse}");
```

</div>
</div>

### Pattern 2: Multi-Step Processing Pipeline

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

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
    model=deployment,
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

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
record MigrationStep(
    [property: JsonPropertyName("step_number")] int StepNumber,
    [property: JsonPropertyName("action")] string Action,
    [property: JsonPropertyName("azure_service")] string AzureService,
    [property: JsonPropertyName("estimated_time")] string EstimatedTime,
    [property: JsonPropertyName("dependencies")] List<string> Dependencies);

record MigrationPlan(
    [property: JsonPropertyName("project_name")] string ProjectName,
    [property: JsonPropertyName("source_platform")] string SourcePlatform,
    [property: JsonPropertyName("target_platform")] string TargetPlatform,
    [property: JsonPropertyName("total_estimated_hours")] int TotalEstimatedHours,
    [property: JsonPropertyName("risk_level")] string RiskLevel,
    [property: JsonPropertyName("steps")] List<MigrationStep> Steps);

const string MigrationSchemaJson = """
    {
        "type": "object",
        "properties": {
            "project_name": { "type": "string" },
            "source_platform": { "type": "string" },
            "target_platform": { "type": "string" },
            "total_estimated_hours": { "type": "integer" },
            "risk_level": { "type": "string" },
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step_number": { "type": "integer" },
                        "action": { "type": "string" },
                        "azure_service": { "type": "string" },
                        "estimated_time": { "type": "string" },
                        "dependencies": { "type": "array", "items": { "type": "string" } }
                    },
                    "required": ["step_number", "action", "azure_service", "estimated_time", "dependencies"],
                    "additionalProperties": false
                }
            }
        },
        "required": [
            "project_name", "source_platform", "target_platform",
            "total_estimated_hours", "risk_level", "steps"
        ],
        "additionalProperties": false
    }
    """;

ChatCompletionOptions migrationOptions = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
        jsonSchemaFormatName: "migration_plan",
        jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(MigrationSchemaJson)),
        jsonSchemaIsStrict: true),
};

ChatCompletion migrationCompletion = client.CompleteChat(
    [
        new SystemChatMessage("""
            You are a cloud migration architect. Create detailed migration plans
            with specific Azure services and time estimates.
            """),
        new UserChatMessage("""
            Plan migration of a Node.js app from Heroku to Azure. It uses
            PostgreSQL, Redis, and has a React frontend with file uploads to S3.
            """),
    ],
    migrationOptions);

MigrationPlan plan = JsonSerializer.Deserialize<MigrationPlan>(migrationCompletion.Content[0].Text)
    ?? throw new InvalidOperationException("Model returned an empty structured response.");

Console.WriteLine($"Migration Plan: {plan.ProjectName}");
Console.WriteLine($"   {plan.SourcePlatform} -> {plan.TargetPlatform}");
Console.WriteLine($"   Risk: {plan.RiskLevel} | Est. Hours: {plan.TotalEstimatedHours}");
Console.WriteLine("\nSteps:");
foreach (MigrationStep step in plan.Steps)
{
    Console.WriteLine($"   {step.StepNumber}. {step.Action}");
    Console.WriteLine($"      Service: {step.AzureService} | Time: {step.EstimatedTime}");
}
```

</div>
</div>

---

## 🎯 Prompt Engineering Best Practices

| Principle | Bad Example | Good Example |
|-----------|-------------|--------------|
| **Be specific** | "Summarize this" | "Summarize in 3 bullet points, max 20 words each" |
| **Set boundaries** | "Answer questions" | "Answer ONLY from the provided context" |
| **Define format** | "List the items" | "Return as a numbered list in markdown" |
| **Handle edge cases** | (nothing) | "If unsure, respond with 'I need more info'" |
| **Use reasoning effort** | Always `reasoning_effort="high"` | `"low"`/`"none"` for simple extraction, `"high"` for multi-step analysis (GPT-5.1 does not support `temperature`) |

---

## 🧪 Challenge Exercise

**Build a "Document Intelligence" pipeline** that:
1. Takes raw unstructured text (email, report, etc.)
2. Extracts entities (people, dates, amounts, organizations)
3. Classifies the document type
4. Generates a structured summary
5. All outputs in validated JSON schema

Use the starter below (paired for Python and .NET) as your `analyze_document` /
`AnalyzeDocument` entry point, then extend it with your own evaluation set and
edge cases -- for example multi-page documents, ambiguous entities, or documents
that don't match any known type.

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
class Entity(BaseModel):
    name: str
    entity_type: str  # person, organization, date, amount, other

class DocumentSummary(BaseModel):
    document_type: str  # email, report, invoice, contract, other
    entities: List[Entity]
    key_points: List[str]
    summary: str

def analyze_document(document_text):
    """Starter for the Document Intelligence challenge -- extend this."""
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": """Analyze the document: classify its type,
            extract named entities (people, organizations, dates, amounts), list the
            key points, and write a concise summary."""},
            {"role": "user", "content": document_text}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document_summary",
                "strict": True,
                "schema": DocumentSummary.model_json_schema()
            }
        }
    )
    return DocumentSummary.model_validate_json(response.choices[0].message.content)

# TODO: extend this with your own evaluation set and edge cases
sample_document = """
Invoice #INV-2026-0447
Dated: March 3, 2026
Billed to: Contoso Retail Group
Amount due: $4,250.00, payable within 30 days.
Prepared by Dana Fields, Accounts Receivable.
"""

result = analyze_document(sample_document)
print(f"Document type: {result.document_type}")
print(f"Entities: {[(e.name, e.entity_type) for e in result.entities]}")
print(f"Key points: {result.key_points}")
print(f"Summary: {result.summary}")
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
record Entity(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("entity_type")] string EntityType);

record DocumentSummary(
    [property: JsonPropertyName("document_type")] string DocumentType,
    [property: JsonPropertyName("entities")] List<Entity> Entities,
    [property: JsonPropertyName("key_points")] List<string> KeyPoints,
    [property: JsonPropertyName("summary")] string Summary);

const string DocumentSchemaJson = """
    {
        "type": "object",
        "properties": {
            "document_type": { "type": "string" },
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" },
                        "entity_type": { "type": "string" }
                    },
                    "required": ["name", "entity_type"],
                    "additionalProperties": false
                }
            },
            "key_points": { "type": "array", "items": { "type": "string" } },
            "summary": { "type": "string" }
        },
        "required": ["document_type", "entities", "key_points", "summary"],
        "additionalProperties": false
    }
    """;

// Starter for the Document Intelligence challenge -- extend this.
DocumentSummary AnalyzeDocument(string documentText)
{
    ChatCompletionOptions options = new()
    {
        ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
            jsonSchemaFormatName: "document_summary",
            jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(DocumentSchemaJson)),
            jsonSchemaIsStrict: true),
    };

    ChatCompletion completion = client.CompleteChat(
        [
            new SystemChatMessage("""
                Analyze the document: classify its type, extract named entities
                (people, organizations, dates, amounts), list the key points, and
                write a concise summary.
                """),
            new UserChatMessage(documentText),
        ],
        options);

    return JsonSerializer.Deserialize<DocumentSummary>(completion.Content[0].Text)
        ?? throw new InvalidOperationException("Model returned an empty structured response.");
}

// TODO: extend this with your own evaluation set and edge cases
const string SampleDocument = """
    Invoice #INV-2026-0447
    Dated: March 3, 2026
    Billed to: Contoso Retail Group
    Amount due: $4,250.00, payable within 30 days.
    Prepared by Dana Fields, Accounts Receivable.
    """;

DocumentSummary result = AnalyzeDocument(SampleDocument);
Console.WriteLine($"Document type: {result.DocumentType}");
Console.WriteLine($"Entities: {string.Join(", ", result.Entities.Select(e => $"{e.Name} ({e.EntityType})"))}");
Console.WriteLine($"Key points: {string.Join("; ", result.KeyPoints)}");
Console.WriteLine($"Summary: {result.Summary}");
```

</div>
</div>

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
