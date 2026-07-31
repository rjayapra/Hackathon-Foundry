// 02-agent-basic - Basic AI Agent with Azure AI Foundry (.NET)
// Lab 3: Models & Agents
//
// The Python counterpart (sample-code/02_agent_basic.py) registers a named,
// versioned "Prompt Agent" in Foundry with the azure-ai-projects package
// (`client.agents.create_version`) and then calls it through the OpenAI
// Responses API. This .NET sample implements the same agent behavior --
// instructions plus a multi-turn conversation -- directly against the OpenAI
// Responses API (already fully supported by the `OpenAI` 2.12.0 package used
// here) without requiring an additional Azure.AI.Projects package dependency.
//
// Agents terminology note: "Classic Agents" (threads + runs) were the original
// Foundry Agent Service surface, modeled on the now-deprecated OpenAI Assistants
// API. This sample intentionally does NOT use that pattern. If you need a
// Foundry-managed, named/versioned agent resource from .NET, use the Foundry
// portal or the Azure.AI.Projects NuGet package (check its current API surface
// before relying on exact method names -- it evolves quickly).
//
// Required environment variables:
//   AZURE_OPENAI_ENDPOINT    e.g. https://your-openai.openai.azure.com/
//   AZURE_OPENAI_DEPLOYMENT  optional, defaults to "gpt-5.1"

using Azure.Identity;
using OpenAI;
using OpenAI.Responses;
using System.ClientModel.Primitives;

#pragma warning disable OPENAI001

string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException(
        "AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env, fill in your " +
        "values, and export them into this process's environment before running (see Lab 2).");

string deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5.1";

const string Instructions = """
    You are a helpful hackathon assistant for Azure AI Foundry.

    Your capabilities:
    - Explain Azure AI concepts clearly
    - Provide code examples
    - Help debug common issues
    - Suggest best practices

    Keep responses concise and practical. Always include code when relevant.
    """;

BearerTokenPolicy tokenPolicy = new(new DefaultAzureCredential(), "https://ai.azure.com/.default");
ResponsesClient client = new(
    tokenPolicy,
    new ResponsesClientOptions { Endpoint = new Uri($"{endpoint.TrimEnd('/')}/openai/v1/") });

Console.WriteLine("Creating AI Agent...");

string[] questions =
[
    "What's the difference between an embedding and a completion model?",
    "Show me a quick example of generating embeddings."
];

string? previousResponseId = null;
foreach (string question in questions)
{
    Console.WriteLine();
    Console.WriteLine(new string('=', 60));
    Console.WriteLine($"User: {question}");
    Console.WriteLine(new string('=', 60));

    CreateResponseOptions options = new()
    {
        Model = deployment,
        Instructions = Instructions,
        PreviousResponseId = previousResponseId,
    };
    options.InputItems.Add(ResponseItem.CreateUserMessageItem(question));

    ResponseResult response = await client.CreateResponseAsync(options);
    previousResponseId = response.Id;

    Console.WriteLine($"\nAssistant:\n{response.GetOutputText()}");
}

Console.WriteLine("\nDone.");
