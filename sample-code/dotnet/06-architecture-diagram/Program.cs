// 06-architecture-diagram - Generate Architecture Diagrams with AI (.NET)
// Lab 3: Models & Agents - Diagram Generation
//
// Uses the Azure AI Foundry OpenAI v1 endpoint with Microsoft Entra ID
// authentication (DefaultAzureCredential) -- no API key is used or required.
// GPT-5.1 is a reasoning model and does not support `Temperature`.
//
// Required environment variables:
//   AZURE_OPENAI_ENDPOINT    e.g. https://your-openai.openai.azure.com/
//   AZURE_OPENAI_DEPLOYMENT  optional, defaults to "gpt-5.1"

using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;

#pragma warning disable OPENAI001

string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException(
        "AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env, fill in your " +
        "values, and export them into this process's environment before running (see Lab 2).");

string deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5.1";

BearerTokenPolicy tokenPolicy = new(new DefaultAzureCredential(), "https://ai.azure.com/.default");
ChatClient client = new(
    model: deployment,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions { Endpoint = new Uri($"{endpoint.TrimEnd('/')}/openai/v1/") });

// --- Demo ---------------------------------------------------------
Console.WriteLine("Architecture Diagram Generator");
Console.WriteLine(new string('=', 60));

// Example 1: RAG Application Architecture
Console.WriteLine("\nExample 1: RAG Application Architecture (Mermaid)");
Console.WriteLine(new string('-', 60));

const string RagDescription = """
    Create an architecture diagram for a RAG-powered chatbot with:
    - React frontend deployed on Azure Static Web Apps
    - Python FastAPI backend on Azure Container Apps
    - Azure AI Foundry for LLM inference (gpt-5.1)
    - Azure AI Search for vector search
    - Azure Blob Storage for document storage
    - Azure Cosmos DB for conversation history
    - User uploads documents which get processed and indexed
    """;

string mermaid = GenerateMermaidDiagram(RagDescription);
Console.WriteLine(mermaid);
await File.WriteAllTextAsync("architecture-rag.mmd", mermaid);
Console.WriteLine("\nSaved to architecture-rag.mmd");

// Example 2: Microservices Architecture
Console.WriteLine("\n\nExample 2: Microservices Architecture (Mermaid)");
Console.WriteLine(new string('-', 60));

const string MicroservicesDescription = """
    Create a microservices architecture diagram with:
    - Azure API Management as the gateway
    - 4 microservices on Azure Container Apps: Users, Orders, Payments, Notifications
    - Azure Service Bus for async communication between services
    - Azure SQL for Users and Orders databases
    - Azure Cosmos DB for Notifications
    - Azure Key Vault for secrets management
    - Azure Monitor for observability
    """;

string mermaid2 = GenerateMermaidDiagram(MicroservicesDescription);
Console.WriteLine(mermaid2);
await File.WriteAllTextAsync("architecture-microservices.mmd", mermaid2);
Console.WriteLine("\nSaved to architecture-microservices.mmd");

// Example 3: PlantUML variant
Console.WriteLine("\n\nExample 3: AI Agent Architecture (PlantUML)");
Console.WriteLine(new string('-', 60));

const string AgentDescription = """
    Create a diagram showing an AI Agent architecture with:
    - User interface (web/mobile)
    - Agent orchestrator (Azure AI Foundry Agent Service)
    - Multiple tools: Code Interpreter, Azure AI Search, Custom API
    - Memory store (Azure Cosmos DB)
    - Model endpoint (gpt-5.1)
    - Evaluation & monitoring layer
    """;

string plantUml = GeneratePlantUmlDiagram(AgentDescription);
Console.WriteLine(plantUml);
await File.WriteAllTextAsync("architecture-agent.puml", plantUml);
Console.WriteLine("\nSaved to architecture-agent.puml");

Console.WriteLine("\n" + new string('=', 60));
Console.WriteLine("Tips:");
Console.WriteLine("  - View .mmd files at https://mermaid.live");
Console.WriteLine("  - View .puml files at https://www.plantuml.com/plantuml/uml");
Console.WriteLine("  - VS Code: Install 'Mermaid Preview' extension");
Console.WriteLine(new string('=', 60));

// Generate a Mermaid architecture diagram from a text description.
// GPT-5.1 does not support `Temperature`, so it is intentionally omitted.
string GenerateMermaidDiagram(string description)
{
    ChatCompletion completion = client.CompleteChat(
        new SystemChatMessage("""
            You are an expert cloud architect who creates architecture diagrams
            in Mermaid syntax.

            Rules:
            - Use 'graph TD' for top-down layouts (most common)
            - Use 'graph LR' for left-right layouts (pipeline/flow)
            - Include proper Azure service names
            - Add descriptive labels on connections
            - Use subgraphs to group related components
            - Output ONLY the Mermaid code, no explanation
            """),
        new UserChatMessage(description));
    return completion.Content[0].Text;
}

// Generate a PlantUML architecture diagram.
// GPT-5.1 does not support `Temperature`, so it is intentionally omitted.
string GeneratePlantUmlDiagram(string description)
{
    ChatCompletion completion = client.CompleteChat(
        new SystemChatMessage("""
            You are an expert cloud architect who creates architecture diagrams
            in PlantUML syntax.

            Rules:
            - Use @startuml and @enduml tags
            - Use proper component diagram notation
            - Include Azure-themed colors (#0078D4 for Azure blue)
            - Label all connections with protocol/purpose
            - Output ONLY the PlantUML code, no explanation
            """),
        new UserChatMessage(description));
    return completion.Content[0].Text;
}
