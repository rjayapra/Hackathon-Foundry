// 03-rag-pipeline - Complete RAG Pipeline (.NET)
// Lab 4: Retrieval-Augmented Generation
//
// .NET counterpart to sample-code/03_rag_pipeline.py: creates a vector + semantic
// search index, chunks and embeds the sample documents, uploads them to Azure AI
// Search (validating every individual result), and answers questions with a hybrid
// semantic vector query grounded by GPT-5.1.
//
// Authenticated entirely with Microsoft Entra ID (DefaultAzureCredential) -- no
// API keys are used or required anywhere in this pipeline.
//
// Required environment variables:
//   AZURE_SEARCH_ENDPOINT               e.g. https://your-search.search.windows.net
//   AZURE_OPENAI_ENDPOINT               e.g. https://your-openai.openai.azure.com/
// Optional environment variables:
//   AZURE_SEARCH_INDEX                  defaults to "hackathon-vector-index"
//   AZURE_OPENAI_DEPLOYMENT             defaults to "gpt-5.1"
//   AZURE_OPENAI_EMBEDDING_DEPLOYMENT   defaults to "text-embedding-3-small"
//   AZURE_OPENAI_EMBEDDING_DIMENSIONS   defaults to "1536"
//
// Run from the repository root so the relative "data/sample-docs" path resolves:
//   dotnet run --project sample-code/dotnet/03-rag-pipeline

using Azure;
using Azure.Identity;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using OpenAI;
using OpenAI.Chat;
using OpenAI.Embeddings;
using System.ClientModel.Primitives;

// BearerTokenPolicy-based authentication is currently marked [Experimental("OPENAI001")]
// in the OpenAI .NET SDK.
#pragma warning disable OPENAI001

// --- Configuration ---
string searchEndpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_ENDPOINT")
    ?? throw new InvalidOperationException(
        "AZURE_SEARCH_ENDPOINT is not set. Copy .env.template to .env, fill in your " +
        "values, and export them into this process's environment before running (see Lab 2).");

string indexName = Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX") ?? "hackathon-vector-index";

string openAiEndpoint = (Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException(
        "AZURE_OPENAI_ENDPOINT is not set. Copy .env.template to .env, fill in your " +
        "values, and export them into this process's environment before running (see Lab 2).")).TrimEnd('/');

string chatDeployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT") ?? "gpt-5.1";
string embeddingDeployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") ?? "text-embedding-3-small";
int embeddingDimensions = int.Parse(Environment.GetEnvironmentVariable("AZURE_OPENAI_EMBEDDING_DIMENSIONS") ?? "1536");

// Microsoft Entra ID authentication -- no API keys anywhere in this pipeline.
DefaultAzureCredential credential = new();
BearerTokenPolicy tokenPolicy = new(credential, "https://ai.azure.com/.default");
Uri openAiV1Endpoint = new($"{openAiEndpoint}/openai/v1/");

ChatClient chatClient = new(
    model: chatDeployment,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions { Endpoint = openAiV1Endpoint });

EmbeddingClient embeddingClient = new(
    model: embeddingDeployment,
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions { Endpoint = openAiV1Endpoint });

SearchIndexClient indexClient = new(new Uri(searchEndpoint), credential);
SearchClient searchClient = new(new Uri(searchEndpoint), indexName, credential);

Console.WriteLine(new string('=', 60));
Console.WriteLine("RAG Pipeline Demo");
Console.WriteLine(new string('=', 60));

// Uncomment these for first run:
// Console.WriteLine("\nStep 1: Creating search index...");
// await CreateIndexAsync();
// Console.WriteLine("\nStep 2: Chunking, embedding, and indexing documents...");
// await IndexDocumentsAsync();

string[] questions =
[
    "What is Contoso's return policy?",
    "How much does the Contoso Watch Pro cost?",
    "My Contoso Buds won't charge. What should I do?",
    "What support tier includes phone support?",
];

foreach (string q in questions)
{
    Console.WriteLine($"\n{new string('-', 60)}");
    Console.WriteLine($"Question: {q}");
    string answer = await RagQueryAsync(q);
    Console.WriteLine($"\nAnswer: {answer}");
}

// --- Helper Functions ---

List<string> ChunkText(string text, int chunkSizeWords = 400, int overlapWords = 80)
{
    // Split text into overlapping word-based chunks.
    string[] words = text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
    List<string> chunks = [];
    int step = chunkSizeWords - overlapWords;
    for (int i = 0; i < words.Length; i += step)
    {
        string chunk = string.Join(' ', words.Skip(i).Take(chunkSizeWords));
        if (!string.IsNullOrWhiteSpace(chunk))
        {
            chunks.Add(chunk);
        }
    }
    return chunks;
}

ReadOnlyMemory<float> GetEmbedding(string text)
{
    // Generate an embedding vector for a text chunk.
    EmbeddingGenerationOptions options = new() { Dimensions = embeddingDimensions };
    OpenAIEmbedding embedding = embeddingClient.GenerateEmbedding(text, options);
    return embedding.ToFloats();
}

// --- Step 1: Create the Search Index ---
async Task CreateIndexAsync()
{
    // Define index schema with a vector field for embeddings.
    List<SearchField> fields =
    [
        new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
        new SearchableField("content"),
        new SearchableField("title") { IsFilterable = true },
        new SimpleField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
        new VectorSearchField("content_vector", embeddingDimensions, "myHnswProfile") { IsHidden = true },
    ];

    VectorSearch vectorSearch = new()
    {
        Algorithms = { new HnswAlgorithmConfiguration("myHnsw") },
        Profiles = { new VectorSearchProfile("myHnswProfile", "myHnsw") },
    };

    SemanticConfiguration semanticConfig = new(
        name: "my-semantic-config",
        prioritizedFields: new SemanticPrioritizedFields
        {
            TitleField = new SemanticField("title"),
            ContentFields = { new SemanticField("content") },
        });

    SearchIndex index = new(indexName)
    {
        Fields = fields,
        VectorSearch = vectorSearch,
        SemanticSearch = new SemanticSearch { Configurations = { semanticConfig } },
    };

    // Fails explicitly (throws) if the server rejects the schema -- for example if
    // embeddingDimensions doesn't match the embedding deployment's actual output size.
    await indexClient.CreateOrUpdateIndexAsync(index);
    Console.WriteLine($"Index '{indexName}' created/updated");
}

// --- Step 2: Chunk, Embed, and Upload Documents ---
async Task IndexDocumentsAsync(string docsPath = "data/sample-docs")
{
    List<SearchDocument> documents = [];
    int docId = 0;

    foreach (string filepath in Directory.GetFiles(docsPath, "*.txt"))
    {
        string content = File.ReadAllText(filepath);
        string filename = Path.GetFileName(filepath);

        foreach (string chunk in ChunkText(content))
        {
            ReadOnlyMemory<float> embedding = GetEmbedding(chunk);
            documents.Add(new SearchDocument
            {
                ["id"] = docId.ToString(),
                ["title"] = filename,
                ["category"] = Path.GetFileNameWithoutExtension(filepath),
                ["content"] = chunk,
                ["content_vector"] = embedding.ToArray(),
            });
            docId++;
            Console.WriteLine($"  Processed chunk {docId} from {filename}");
        }
    }

    Response<IndexDocumentsResult> response = await searchClient.UploadDocumentsAsync(documents);

    // Validate every individual result -- a batch call can partially fail even when
    // the overall request succeeds. Fail explicitly rather than silently dropping
    // documents from the index.
    List<IndexingResult> failures = response.Value.Results.Where(r => !r.Succeeded).ToList();
    if (failures.Count > 0)
    {
        string details = string.Join("; ", failures.Select(f => $"{f.Key}: {f.ErrorMessage}"));
        throw new InvalidOperationException($"Failed to upload search documents: {details}");
    }

    Console.WriteLine($"Uploaded {response.Value.Results.Count} chunks to index '{indexName}'");
}

// --- Step 3: RAG Query ---
async Task<string> RagQueryAsync(string question)
{
    // Step 1: Embed the question
    ReadOnlyMemory<float> questionEmbedding = GetEmbedding(question);

    // Step 2: Search the index (hybrid: keyword + vector), reranked with semantic search
    SearchOptions searchOptions = new()
    {
        VectorSearch = new()
        {
            Queries =
            {
                new VectorizedQuery(questionEmbedding)
                {
                    KNearestNeighborsCount = 50,
                    Fields = { "content_vector" },
                },
            },
        },
        SemanticSearch = new SemanticSearchOptions { SemanticConfigurationName = "my-semantic-config" },
        QueryType = SearchQueryType.Semantic,
        Select = { "id", "title", "category", "content" },
        Size = 5,
    };

    SearchResults<SearchDocument> results = await searchClient.SearchAsync<SearchDocument>(question, searchOptions);

    // Step 3: Collect retrieved context with source labels for citations
    List<string> contextParts = [];
    int rank = 0;
    Console.WriteLine("\n  Retrieved sources:");
    await foreach (SearchResult<SearchDocument> result in results.GetResultsAsync())
    {
        rank++;
        string sourceId = $"S{rank}";
        string title = result.Document["title"]?.ToString() ?? "";
        string content = result.Document["content"]?.ToString() ?? "";
        contextParts.Add($"[{sourceId}] Title: {title}\n{content}");

        double score = result.SemanticSearch?.RerankerScore ?? result.Score ?? 0.0;
        Console.WriteLine($"     [{sourceId}] {title} (score: {score:F2})");
    }

    string context = string.Join("\n\n---\n\n", contextParts);

    // Step 4: Generate a grounded answer with GPT-5.1 (a reasoning model -- no Temperature)
    string instructions = $"""
        Answer the user's question using only the provided context. Cite supporting
        sources using their labels, such as [S1]. If the context doesn't contain the
        answer, say "I don't have enough information to answer that."

        Context:
        {context}
        """;

    ChatCompletionOptions chatOptions = new()
    {
        ReasoningEffortLevel = ChatReasoningEffortLevel.Low,
        MaxOutputTokenCount = 800,
    };

    ChatCompletion completion = chatClient.CompleteChat(
        [
            new DeveloperChatMessage(instructions),
            new UserChatMessage(question),
        ],
        chatOptions);

    return completion.Content[0].Text;
}
