// 01-hello-foundry - Your first Azure AI Foundry API call (.NET)
// Lab 2: Tooling & Setup
//
// Calls the Azure AI Foundry OpenAI v1 endpoint ("{endpoint}/openai/v1/") using the
// plain OpenAI SDK, authenticated with Microsoft Entra ID via DefaultAzureCredential.
// No API key is used or required.
//
// Required environment variables:
//   AZURE_OPENAI_ENDPOINT    e.g. https://your-openai.openai.azure.com/
//   AZURE_OPENAI_DEPLOYMENT  optional, defaults to "gpt-5.1"

using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;

// BearerTokenPolicy-based authentication is currently marked [Experimental("OPENAI001")]
// in the OpenAI .NET SDK.
#pragma warning disable OPENAI001

string endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException(
        "AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env, fill in your " +
        "values, and export them into this process's environment before running (see Lab 2).");

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

// GPT-5.1 is a reasoning model: no `Temperature`, use `MaxOutputTokenCount`
// instead of the older `MaxTokens` concept.
ChatCompletionOptions options = new()
{
    MaxOutputTokenCount = 200
};

ChatCompletion completion = client.CompleteChat(
    [
        new SystemChatMessage("You are a helpful assistant."),
        new UserChatMessage("What is Azure AI Foundry? Explain in 3 sentences.")
    ],
    options);

Console.WriteLine(new string('=', 60));
Console.WriteLine("Hello from Azure AI Foundry!");
Console.WriteLine(new string('=', 60));
Console.WriteLine($"\nResponse:\n{completion.Content[0].Text}");
Console.WriteLine("\nToken usage:");
Console.WriteLine($"   Prompt tokens:     {completion.Usage.InputTokenCount}");
Console.WriteLine($"   Completion tokens: {completion.Usage.OutputTokenCount}");
Console.WriteLine($"   Total tokens:      {completion.Usage.TotalTokenCount}");
Console.WriteLine($"\nModel: {completion.Model}");
