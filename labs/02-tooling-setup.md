# Lab 2: Tooling & Setup

## 🎯 Learning Objectives

By the end of this lab, you will:
- Have a fully configured development environment
- Understand the SDK ecosystem and when to use each SDK
- Be able to authenticate and make your first API call
- Know how to use the Azure CLI for Foundry operations

---

## 📑 Table of Contents

| # | Exercise | Type |
|---|----------|------|
| 1 | [SDK Ecosystem Overview](#sdk-ecosystem-overview) | Concepts |
| 2 | [Step 1: Install Required Tools](#step-1-install-required-tools) | 🐍/.NET CLI |
| 3 | [Step 2: Create Project Directory](#step-2-create-project-directory) | 🐍/.NET CLI |
| 4 | [Step 3: Install Packages](#step-3-install-packages) | 🐍/.NET CLI |
| 5 | [Step 4: Configure Environment Variables](#step-4-configure-environment-variables) | 🐍/.NET CLI / 🌐 Portal |
| 6 | [First API Call — Portal Option](#-option-a-first-api-call-in-the-playground-no-code) | 🌐 Portal |
| 7 | [First API Call — Code Option](#-️-net--option-b-first-api-call-with-code) | 🐍/.NET Code |
| 8 | [Azure CLI for Foundry](#️-azure-cli-for-foundry) | 🐍 CLI |
| 9 | [Authentication Methods Comparison](#-authentication-methods-comparison) | Reference |

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

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

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

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```bash
# Verify .NET SDK version (need 8.0+)
dotnet --version

# Verify Azure CLI
az --version

# Login to Azure
az login

# Set your subscription (if multiple)
az account set --subscription "<your-subscription-id>"
```

</div>
</div>

### Step 2: Create Project Directory

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```bash
mkdir hackathon-foundry && cd hackathon-foundry
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```bash
mkdir hackathon-foundry && cd hackathon-foundry
dotnet new console -n HackathonFoundry
cd HackathonFoundry
```

> The `dotnet new console` template targets the SDK you have installed. Make sure
> your `.csproj` sets `<TargetFramework>net8.0</TargetFramework>` (see the sample
> projects under `sample-code/dotnet/` in this repo for working examples).

</div>
</div>

### Step 3: Install Packages

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```bash
pip install azure-ai-projects azure-identity openai python-dotenv
pip install azure-search-documents azure-storage-blob
pip install streamlit pandas
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```bash
dotnet add package OpenAI --version 2.12.0
dotnet add package Azure.Identity --version 1.21.0
```

> These are the two packages used throughout the .NET samples in this hackathon:
> the official `OpenAI` client (talking directly to the Azure AI Foundry `/openai/v1`
> endpoint) and `Azure.Identity` for Entra ID authentication (`DefaultAzureCredential`).
> No `Azure.AI.OpenAI` wrapper package and no API keys are required.

</div>
</div>

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
AZURE_OPENAI_DEPLOYMENT=gpt-5.1
```

> 💡 **Where to find these values:**
> - **Project Endpoint**: Foundry Portal → Your Project → Overview → "Project endpoint"
> - **OpenAI Endpoint**: Azure Portal → Your OpenAI resource → Keys and Endpoint
> - **Deployment name**: Foundry Portal → Deployments → Name column
>
> Every sample in this hackathon (Python and .NET) authenticates with Microsoft Entra ID
> (`DefaultAzureCredential`) instead of an API key, so you will **not** set
> `AZURE_OPENAI_API_KEY` — the `az login` session from Step 1 is all you need.
> **.NET note:** console apps read these as OS process environment variables via
> `Environment.GetEnvironmentVariable(...)`, not from the `.env` file directly. Either
> `export`/`set` the values in your shell before `dotnet run`, or add a small `.env`
> loader package (e.g. `dotenv.net`) if you want file-based config like the Python samples.

---

## 🖥️ Hands-On: First API Call

### 🌐 Option A: First API Call in the Playground (No Code)

> Perfect if you want to verify your setup is working before writing any code.

1. Go to [ai.azure.com](https://ai.azure.com) → your project
2. Click **Playgrounds** → **Chat**
3. Select your deployed model (e.g., **GPT-5.1** or **GPT-5-mini**)
4. In the **System message** box, type:
   ```
   You are a helpful assistant.
   ```
5. In the chat input, type:
   ```
   What is Azure AI Foundry? Explain in 2 sentences.
   ```
6. Press **Send** and observe the response
7. Note the **token usage** — this is what you'll be billed for
8. Try adjusting:
   - **Max Completion response**: Set to `50` — see how the response gets cut short   

> ✅ If you see a response, your Foundry setup is working! You can proceed with either portal or code path from here.

---

### 🐍 / .NET — Option B: First API Call with Code

### Step 5: Hello Foundry — Using the OpenAI v1 API + Entra ID

Both languages below call the same Azure AI Foundry OpenAI **v1** endpoint
(`{AZURE_OPENAI_ENDPOINT}/openai/v1`) and authenticate with Microsoft Entra ID via
`DefaultAzureCredential` — **no API key is used anywhere**. GPT-5.1 is a reasoning
model, so the calls use `max_completion_tokens` (not `max_tokens`) and omit
`temperature` entirely (GPT-5.1 does not support it).

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

Create `01_hello_foundry.py`:

```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")

# Microsoft Entra ID authentication -- no API key needed.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)

# Plain OpenAI client pointed at the Foundry resource's v1 endpoint.
client = OpenAI(
    base_url=f"{endpoint.rstrip('/')}/openai/v1",
    api_key=token_provider,
)

# GPT-5.1 is a reasoning model: no `temperature`, use `max_completion_tokens`.
response = client.chat.completions.create(
    model=deployment,  # Your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Azure AI Foundry? Explain in 2 sentences."}
    ],
    max_completion_tokens=200
)

print("Response from Azure AI Foundry:")
print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

Run it:
```bash
python 01_hello_foundry.py
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

`Program.cs` (see `sample-code/dotnet/01-hello-foundry/` for the full project):

```csharp
using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;

// BearerTokenPolicy is currently marked [Experimental("OPENAI001")] in the OpenAI SDK.
#pragma warning disable OPENAI001

string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("Set AZURE_OPENAI_ENDPOINT.");
string deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5.1";

// Microsoft Entra ID authentication -- no API key needed.
BearerTokenPolicy tokenPolicy = new(
    new DefaultAzureCredential(),
    "https://ai.azure.com/.default");

ChatClient client = new(
    model: deployment,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions
    {
        Endpoint = new Uri($"{endpoint.TrimEnd('/')}/openai/v1/")
    });

// GPT-5.1 is a reasoning model: no `Temperature`, use `MaxOutputTokenCount`.
ChatCompletionOptions options = new()
{
    MaxOutputTokenCount = 200
};

ChatCompletion completion = client.CompleteChat(
    [
        new SystemChatMessage("You are a helpful assistant."),
        new UserChatMessage("What is Azure AI Foundry? Explain in 2 sentences.")
    ],
    options);

Console.WriteLine("Response from Azure AI Foundry:");
Console.WriteLine(completion.Content[0].Text);
Console.WriteLine($"\nTokens used: {completion.Usage.TotalTokenCount}");
```

Run it:
```bash
dotnet run
```

</div>
</div>

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
  --deployment-name gpt-5.1 \
  --model-name gpt-5.1 \
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
- [ ] Your Python or .NET environment is set up with all packages installed
- [ ] `.env` file is configured with your endpoints (no API key needed)
- [ ] You can successfully run the Hello Foundry sample and get a response
- [ ] You understand the difference between API key and Entra ID auth

---

**Next:** [Lab 3 — Models & Agents →](03-models-and-agents.md)
