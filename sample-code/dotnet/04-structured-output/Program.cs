// 04-structured-output - Structured Outputs with JSON Schema (.NET)
// Lab 5: Prompt Engineering & Structured Outputs
//
// .NET counterpart to sample-code/04_structured_output.py: JSON mode, then strict
// JSON-schema structured outputs deserialized into typed records with
// System.Text.Json (the Pydantic equivalent for this SDK).
//
// Authenticated with Microsoft Entra ID (DefaultAzureCredential) -- no API key is
// used or required. GPT-5.1 is a reasoning model, so none of these calls set
// `Temperature`.
//
// Required environment variables:
//   AZURE_OPENAI_ENDPOINT    e.g. https://your-openai.openai.azure.com/
// Optional environment variables:
//   AZURE_OPENAI_DEPLOYMENT  defaults to "gpt-5.1"

using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

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

Console.WriteLine("Structured Outputs Demo");
Console.WriteLine("Using Azure AI Foundry with strict JSON schema validation\n");

ExampleJsonMode();
ExampleStructuredOutput();
ExampleMultiExtraction();

Console.WriteLine("\n" + new string('=', 60));
Console.WriteLine("All examples completed successfully!");
Console.WriteLine(new string('=', 60));

// --- Example 1: Simple JSON Mode ---
void ExampleJsonMode()
{
    Console.WriteLine("\n" + new string('=', 60));
    Console.WriteLine("Example 1: Simple JSON Mode");
    Console.WriteLine(new string('=', 60));

    const string SystemPrompt = """
        Extract the product review into JSON with fields:
        product_name, rating (1-5), pros (array), cons (array), recommendation (boolean)
        """;
    const string UserReview = """
        I bought the Contoso Buds last month and I'm impressed! The noise cancellation
        is excellent and battery lasts all day. Sound quality is rich and balanced. My
        only complaints are the case is a bit bulky and they occasionally disconnect
        during calls. Overall, I'd recommend them. 4 out of 5 stars.
        """;

    ChatCompletionOptions options = new()
    {
        ResponseFormat = ChatResponseFormat.CreateJsonObjectFormat(),  // Forces JSON output
        MaxOutputTokenCount = 500,
    };

    ChatCompletion completion = client.CompleteChat(
        [
            new SystemChatMessage(SystemPrompt),
            new UserChatMessage(UserReview),
        ],
        options);

    using JsonDocument result = JsonDocument.Parse(completion.Content[0].Text);
    Console.WriteLine(JsonSerializer.Serialize(result.RootElement, new JsonSerializerOptions { WriteIndented = true }));
}

// --- Example 2: Strict JSON Schema Validation ---
void ExampleStructuredOutput()
{
    Console.WriteLine("\n" + new string('=', 60));
    Console.WriteLine("Example 2: Schema-Enforced Structured Output");
    Console.WriteLine(new string('=', 60));

    const string TicketText = """
        Subject: URGENT - Charged 3 times for Contoso Watch Pro!!

        Hi, I'm absolutely furious. I ordered ONE Contoso Watch Pro on June 1st
        but my credit card shows THREE charges of $349.99. That's over $1000
        taken from my account! I need this resolved TODAY or I'm disputing with
        my bank and leaving a review everywhere.

        Order #CNT-2026-78432
        - Sarah Mitchell
        """;

    const string SchemaJson = """
        {
            "type": "object",
            "properties": {
                "ticket_id": { "type": "string" },
                "category": { "type": "string" },
                "priority": { "type": "string" },
                "sentiment": { "type": "string" },
                "customer_name": { "type": ["string", "null"] },
                "product_mentioned": { "type": ["string", "null"] },
                "summary": { "type": "string" },
                "suggested_action": { "type": "string" },
                "requires_escalation": { "type": "boolean" }
            },
            "required": [
                "ticket_id", "category", "priority", "sentiment", "customer_name",
                "product_mentioned", "summary", "suggested_action", "requires_escalation"
            ],
            "additionalProperties": false
        }
        """;

    ChatCompletionOptions options = new()
    {
        ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
            jsonSchemaFormatName: "support_ticket",
            jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(SchemaJson)),
            jsonSchemaIsStrict: true),
    };

    ChatCompletion completion = client.CompleteChat(
        [
            new SystemChatMessage("""
                You are a support ticket classifier. Analyze the ticket and extract
                structured information. Use ticket_id from the order number if
                available, otherwise generate one.
                """),
            new UserChatMessage(TicketText),
        ],
        options);

    // Guaranteed to match the schema -- fail explicitly if the SDK ever returns
    // an empty payload instead of silently continuing with a null ticket.
    SupportTicket ticket = JsonSerializer.Deserialize<SupportTicket>(completion.Content[0].Text)
        ?? throw new InvalidOperationException("Model returned an empty structured response.");

    Console.WriteLine($"  Ticket ID: {ticket.TicketId}");
    Console.WriteLine($"  Category: {ticket.Category}");
    Console.WriteLine($"  Priority: {ticket.Priority}");
    Console.WriteLine($"  Sentiment: {ticket.Sentiment}");
    Console.WriteLine($"  Customer: {ticket.CustomerName}");
    Console.WriteLine($"  Product: {ticket.ProductMentioned}");
    Console.WriteLine($"  Summary: {ticket.Summary}");
    Console.WriteLine($"  Action: {ticket.SuggestedAction}");
    Console.WriteLine($"  Escalate: {ticket.RequiresEscalation}");
}

// --- Example 3: Multi-Item Extraction ---
void ExampleMultiExtraction()
{
    Console.WriteLine("\n" + new string('=', 60));
    Console.WriteLine("Example 3: Multi-Item Extraction");
    Console.WriteLine(new string('=', 60));

    const string CatalogText = """
        New arrivals this season! The Contoso Hub ($149.99) is our flagship smart home
        controller with voice activation and 200+ integrations - 2 year warranty.
        Also check out the Contoso Watch Pro at $349.99 - it's got ECG, SpO2, and
        5-day battery life with a 2 year warranty. For audio lovers, the Contoso
        Speaker Max ($199.99) delivers spatial audio with a built-in voice assistant,
        covered by our standard 2-year warranty.
        """;

    const string SchemaJson = """
        {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": { "type": "string" },
                            "category": { "type": "string" },
                            "price": { "type": "number" },
                            "key_features": { "type": "array", "items": { "type": "string" } },
                            "warranty_years": { "type": "integer" }
                        },
                        "required": ["name", "category", "price", "key_features", "warranty_years"],
                        "additionalProperties": false
                    }
                },
                "total_count": { "type": "integer" }
            },
            "required": ["products", "total_count"],
            "additionalProperties": false
        }
        """;

    ChatCompletionOptions options = new()
    {
        ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
            jsonSchemaFormatName: "product_catalog",
            jsonSchema: BinaryData.FromBytes(Encoding.UTF8.GetBytes(SchemaJson)),
            jsonSchemaIsStrict: true),
    };

    ChatCompletion completion = client.CompleteChat(
        [
            new SystemChatMessage("Extract all products mentioned with their details."),
            new UserChatMessage(CatalogText),
        ],
        options);

    ProductCatalog catalog = JsonSerializer.Deserialize<ProductCatalog>(completion.Content[0].Text)
        ?? throw new InvalidOperationException("Model returned an empty structured response.");

    Console.WriteLine($"\n  Found {catalog.TotalCount} products:\n");
    foreach (ProductSpec p in catalog.Products)
    {
        Console.WriteLine($"  {p.Name} ({p.Category})");
        Console.WriteLine($"     ${p.Price:F2} | {p.WarrantyYears}yr warranty");
        Console.WriteLine($"     {string.Join(", ", p.KeyFeatures.Take(3))}");
        Console.WriteLine();
    }
}

// --- Data Contracts (the .NET equivalent of the Python Pydantic models) ---
record SupportTicket(
    [property: JsonPropertyName("ticket_id")] string TicketId,
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("priority")] string Priority,
    [property: JsonPropertyName("sentiment")] string Sentiment,
    [property: JsonPropertyName("customer_name")] string? CustomerName,
    [property: JsonPropertyName("product_mentioned")] string? ProductMentioned,
    [property: JsonPropertyName("summary")] string Summary,
    [property: JsonPropertyName("suggested_action")] string SuggestedAction,
    [property: JsonPropertyName("requires_escalation")] bool RequiresEscalation);

record ProductSpec(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("price")] double Price,
    [property: JsonPropertyName("key_features")] List<string> KeyFeatures,
    [property: JsonPropertyName("warranty_years")] int WarrantyYears);

record ProductCatalog(
    [property: JsonPropertyName("products")] List<ProductSpec> Products,
    [property: JsonPropertyName("total_count")] int TotalCount);
