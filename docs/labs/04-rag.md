# Lab 4: RAG — Retrieval-Augmented Generation

## 🎯 Learning Objectives

By the end of this lab, you will:
- Understand how RAG works and why it matters
- Create an Azure AI Search index with your documents
- Generate embeddings for vector and hybrid search
- Build a complete RAG pipeline that gives grounded answers

---

## 📑 Table of Contents

| # | Exercise | Type |
|---|----------|------|
| 1 | [What is RAG?](#what-is-rag) | Concepts |
| 2 | [Step 1: Create Azure AI Search Resource](#step-1-create-an-azure-ai-search-resource) | 🌐 Portal |
| 3 | [Step 2: Create Storage & Upload Documents](#step-2-create-a-storage-account--upload-documents) | 🌐 Portal |
| 4 | [Step 3: Import and Vectorize Data](#step-3-import-and-vectorize-data-for-rag) | 🌐 Portal |
| 5 | [Step 4: Validate Retrieval](#step-4-validate-retrieval) | 🌐 Portal |
| 6 | [Step 5: Create a Foundry IQ Knowledge Base](#step-5-create-a-foundry-iq-knowledge-base) | 🌐 Portal |
| 7 | [Step 6: Connect and Test an Agent](#step-6-connect-and-test-an-agent) | 🌐 Portal |
| 8 | [RAG with Code — Prepare Documents](#step-1-prepare-sample-documents) | 🐍 Code |
| 9 | [RAG with Code — Create Embeddings](#step-2-upload-documents-and-create-embeddings) | 🐍 Code |
| 10 | [RAG with Code — Chunk & Embed](#step-3-chunk-documents-and-generate-embeddings) | 🐍 Code |
| 11 | [RAG with Code — Upload to Search](#step-4-upload-to-azure-ai-search) | 🐍 Code |
| 12 | [RAG with Code — Query Pipeline](#step-5-query-with-rag) | 🐍 Code |
| 13 | [Search Strategies Comparison](#-search-strategies-comparison) | Reference |
| 14 | [🧪 Challenge Exercise](#-challenge-exercise) | Challenge |

---

## What is RAG?

**RAG (Retrieval-Augmented Generation)** grounds a model with relevant, current, or private information retrieved at query time. This is especially useful for information that isn't in the model's training data or shouldn't be encoded in the model itself.

### The Problem Without RAG
```
User: "What is our company's refund policy?"
LLM:  "I don't have specific information about your company's policies..." ❌
```

### The Solution With RAG
```
User: "What is our company's refund policy?"
RAG:  [Retrieves relevant policy document from your knowledge base]
LLM:  "According to your policy document, refunds are available within 30 days..." ✅
```

### How RAG Works — Pipeline

```
┌─────────────────── INDEXING (One-time) ───────────────────┐
│                                                            │
│  Documents → Chunk → Generate Embeddings → Store in Index  │
│                                                            │
└────────────────────────────────────────────────────────────┘

┌─────────────────── QUERY TIME ────────────────────────────┐
│                                                            │
│  User Query → Embed Query → Search Index → Top Results     │
│       │                                          │         │
│       └──── Combine Query + Results → LLM → Answer ────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Hands-On: Build a RAG Pipeline

### 🌐 Option A: Set Up RAG via the Azure & Foundry Portals (No Code)

> This is the fastest no-code path: create a vectorized search index, expose it
> through a Foundry IQ knowledge base, and test grounded answers with an agent.

---

#### Step 1: Create an Azure AI Search Resource

1. Go to the [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource** → search for **"Azure AI Search"**
3. Click **Create** and fill in:
   - **Subscription**: Your subscription
   - **Resource group**: Your hackathon resource group
   - **Service name**: `hackathon-search-<yourname>` (must be globally unique)
   - **Location**: Same region as your Foundry resource
   - **Pricing tier**: **Free** (for hackathon) or **Basic** (for production)
4. Click **Review + Create** → **Create**
5. Wait for deployment to complete (~2 minutes)

#### Step 2: Create a Storage Account & Upload Documents

1. In the Azure Portal, go to **+ Create a resource** → **Storage account**
2. Create with settings:
   - **Name**: `hackathonstorage<yourname>`
   - **Region**: Same as above
   - **Performance**: Standard
   - **Redundancy**: LRS (cheapest)
3. Click **Create**
4. Once created, go to the storage account → **Containers** → **+ Container**
   - **Name**: `documents`
   - **Access level**: Private
5. Open the `documents` container → **Upload**
6. Upload all files from `data/sample-docs/`:
   - `product-overview.txt`
   - `support-policy.txt`
   - `troubleshooting-guide.txt`

#### Step 3: Import and Vectorize Data for RAG

Use the current Azure AI Search
[**Import data** wizard](https://learn.microsoft.com/azure/search/search-get-started-portal-import-vectors).
It creates the data source, skillset, index, vectorizer, and indexer needed for
integrated vectorization.

1. Open your **Azure AI Search** resource in the Azure portal.
2. On **Overview**, select **Import data**.
3. Select **Azure Blob Storage**, then select the **RAG** scenario.
4. Connect to the `documents` container.
5. Select **Authenticate using managed identity** and keep **System-assigned**.
   Complete any role-assignment prompts shown by the wizard.
6. For text vectorization:
   - Select your Azure OpenAI or Foundry resource.
   - Select a deployed `text-embedding-3-small` or `text-embedding-3-large` model.
   - Keep the same embedding deployment for indexing and query-time vectorization.
7. Configure the index:
   - **Index name**: `hackathon-vector-index`
   - Enable semantic ranking if your search tier supports it.
   - Review the generated chunk, title, source, and vector fields.
8. Create the objects and wait for the indexer to finish.

> 💡 **Integrated vectorization** handles chunking and embedding during indexing and
> vectorizes text queries with the same model at query time. Schedule the indexer in
> production so changed documents are picked up automatically.

#### Step 4: Validate Retrieval

1. Go to **Indexes** → `hackathon-vector-index` → **Search explorer**.
2. Run `*` to confirm that chunked documents were indexed.
3. Test these queries:
   - `return policy`
   - `Contoso Buds not charging`
   - `support tier with phone support`
4. Compare keyword, vector, hybrid, and hybrid with semantic ranking when those
   options are available.
5. Confirm that returned chunks contain the source path or title needed for citations.

#### Step 5: Create a Foundry IQ Knowledge Base

> ⚠️ **Azure OpenAI On Your Data is deprecated and retires October 14, 2026.**
> For new solutions, use
> [**Foundry IQ**](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq)
> with Foundry Agent Service.

1. Go to [Microsoft Foundry](https://ai.azure.com) and turn on **New Foundry**.
2. Open your project and select **Build**.
3. On the **Knowledge** tab, connect your Azure AI Search service.
4. Create a knowledge base and add the indexed Azure AI Search content as a
   knowledge source.
5. Configure retrieval behavior. Start with hybrid retrieval and semantic ranking,
   then tune it against representative questions.

> Foundry IQ can plan and decompose queries, retrieve across one or more knowledge
> sources, apply ranking, and return grounded results with citations. Some agentic
> retrieval capabilities remain in preview.

#### Step 6: Connect and Test an Agent

1. On the **Agents** tab, create or open an agent that uses your GPT-5.1 deployment.
2. Connect the Foundry IQ knowledge base to the agent.
3. In the playground, ask:
   - *"What is Contoso's return policy?"*
   - *"How do I fix my Contoso Buds not charging?"*
   - *"What support tier includes phone support?"*
4. Verify that answers are grounded and include citations.
5. Ask an out-of-scope question and confirm that the agent says the knowledge base
   doesn't contain enough information.

---

### 🐍 / .NET Option B: Build RAG with Code (Code-First)

> For developers who want full control over the RAG pipeline.

### Step 1: Prepare Sample Documents

Create a folder `data/sample-docs/` with some text files. Here's sample content:

**`data/sample-docs/product-overview.txt`**
```
Contoso Electronics Product Overview

Contoso Electronics is a leader in consumer electronics, offering:
- Smart Home Devices: Contoso Hub, Contoso Thermostat, Contoso Camera
- Wearables: Contoso Watch Pro, Contoso Band
- Audio: Contoso Buds, Contoso Speaker Max

All products come with a 2-year warranty and 30-day money-back guarantee.
Products can be returned to any Contoso retail location or shipped back prepaid.
```

**`data/sample-docs/support-policy.txt`**
```
Contoso Electronics Support Policy

Support Tiers:
1. Basic (Free): Email support, 48-hour response time
2. Premium ($9.99/month): Phone + email, 4-hour response time
3. Enterprise (Custom): Dedicated support engineer, 1-hour SLA

Warranty Coverage:
- Hardware defects: Full replacement
- Software issues: Free updates for 2 years
- Accidental damage: Not covered (see insurance options)

Return Policy:
- 30 days from purchase for full refund
- Product must be in original packaging
- Opened software is non-refundable
```

### Step 2: Upload Documents and Create Embeddings

Install current packages, sign in with Azure CLI, and use Microsoft Entra ID rather
than storing service keys:

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```powershell
pip install --upgrade openai azure-identity azure-search-documents python-dotenv
az login
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```powershell
dotnet add package OpenAI --version 2.12.0
dotnet add package Azure.Identity --version 1.21.0
dotnet add package Azure.Search.Documents --version 12.0.0
az login
```

</div>
</div>

Your identity needs **Cognitive Services OpenAI User** for model inference and
appropriate Azure AI Search data-plane roles to create the index, upload documents,
and run queries.

Configure these values in `.env`. Deployment values are deployment names, which
can differ from model names:

```dotenv
AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-gpt-5.1-deployment>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<your-text-embedding-3-small-deployment>
AZURE_OPENAI_EMBEDDING_DIMENSIONS=1536
AZURE_SEARCH_ENDPOINT=https://<search-service-name>.search.windows.net
AZURE_SEARCH_INDEX=hackathon-vector-index
```

The code uses the
[Azure OpenAI v1 API](https://learn.microsoft.com/azure/ai-foundry/openai/api-version-lifecycle),
which doesn't require a dated `api-version`.

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
)

load_dotenv()

# --- Configuration ---
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "hackathon-vector-index")
OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")
EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
    "text-embedding-3-small",
)
EMBEDDING_DIMENSIONS = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "1536"))

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential,
    "https://ai.azure.com/.default",
)

OPENAI_BASE_URL = (
    f"{OPENAI_ENDPOINT}/"
    if OPENAI_ENDPOINT.endswith("/openai/v1")
    else f"{OPENAI_ENDPOINT}/openai/v1/"
)
openai_client = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=token_provider,
)

# --- Step 2a: Create the Search Index ---
index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential,
)

# Define index schema with vector field for embeddings
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="title", type=SearchFieldDataType.String, filterable=True),
    SimpleField(
        name="category",
        type=SearchFieldDataType.String,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        retrievable=False,
        vector_search_dimensions=EMBEDDING_DIMENSIONS,
        vector_search_profile_name="myHnswProfile",
    ),
]

# Configure vector search
vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
        )
    ],
)

# Configure semantic ranking for hybrid queries
semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="content")],
    ),
)
semantic_search = SemanticSearch(configurations=[semantic_config])

# Create the index
index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
)

index_client.create_or_update_index(index=index)
print(f"✅ Index '{INDEX_NAME}' created/updated")
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
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
// in the OpenAI .NET SDK. All the usings above are shared by Steps 2-5 below --
// they must stay together at the top of Program.cs.
#pragma warning disable OPENAI001

// --- Configuration ---
string searchEndpoint = Environment.GetEnvironmentVariable("AZURE_SEARCH_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_SEARCH_ENDPOINT is not set.");
string indexName = Environment.GetEnvironmentVariable("AZURE_SEARCH_INDEX") ?? "hackathon-vector-index";
string openAiEndpoint = (Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.")).TrimEnd('/');
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

// --- Step 2a: Create the Search Index ---
SearchIndexClient indexClient = new(new Uri(searchEndpoint), credential);

// Define index schema with a vector field for embeddings
List<SearchField> fields =
[
    new SimpleField("id", SearchFieldDataType.String) { IsKey = true },
    new SearchableField("content"),
    new SearchableField("title") { IsFilterable = true },
    new SimpleField("category", SearchFieldDataType.String) { IsFilterable = true, IsFacetable = true },
    new VectorSearchField("content_vector", embeddingDimensions, "myHnswProfile") { IsHidden = true },
];

// Configure vector search
VectorSearch vectorSearch = new()
{
    Algorithms = { new HnswAlgorithmConfiguration("myHnsw") },
    Profiles = { new VectorSearchProfile("myHnswProfile", "myHnsw") },
};

// Configure semantic ranking for hybrid queries
SemanticConfiguration semanticConfig = new(
    name: "my-semantic-config",
    prioritizedFields: new SemanticPrioritizedFields
    {
        TitleField = new SemanticField("title"),
        ContentFields = { new SemanticField("content") },
    });
SemanticSearch semanticSearch = new()
{
    Configurations = { semanticConfig },
};

// Create the index
SearchIndex index = new(indexName)
{
    Fields = fields,
    VectorSearch = vectorSearch,
    SemanticSearch = semanticSearch,
};

await indexClient.CreateOrUpdateIndexAsync(index);
Console.WriteLine($"Index '{indexName}' created/updated");
```

> `VectorSearchField` fails explicitly at index-creation time on the server if
> `embeddingDimensions` doesn't match your embedding deployment's actual output size.

</div>
</div>

> `text-embedding-3-small` produces up to 1,536 dimensions and
> `text-embedding-3-large` produces up to 3,072. The index field dimension must
> exactly match the dimension returned by your embedding deployment.

### Step 3: Chunk Documents and Generate Embeddings

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
def chunk_text(text, chunk_size_words=400, overlap_words=80):
    """Split text into overlapping word-based chunks for this lab."""
    words = text.split()
    chunks = []
    step = chunk_size_words - overlap_words
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size_words])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_embedding(text):
    """Generate embedding for a text chunk."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding

# Process all documents
documents = []
doc_id = 0

for filepath in Path("data/sample-docs").glob("*.txt"):
    content = filepath.read_text(encoding="utf-8")
    filename = filepath.name
    chunks = chunk_text(content)
    
    for chunk in chunks:
        embedding = get_embedding(chunk)
        documents.append({
            "id": str(doc_id),
            "title": filename,
            "category": filepath.stem,
            "content": chunk,
            "content_vector": embedding,
        })
        doc_id += 1
        print(f"  📄 Processed chunk {doc_id} from {filename}")

print(f"\n✅ Total chunks to index: {len(documents)}")
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
List<string> ChunkText(string text, int chunkSizeWords = 400, int overlapWords = 80)
{
    // Split text into overlapping word-based chunks for this lab.
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
    // Generate embedding for a text chunk.
    EmbeddingGenerationOptions options = new() { Dimensions = embeddingDimensions };
    OpenAIEmbedding embedding = embeddingClient.GenerateEmbedding(text, options);
    return embedding.ToFloats();
}

// Process all documents
List<SearchDocument> documents = [];
int docId = 0;

foreach (string filepath in Directory.GetFiles("data/sample-docs", "*.txt"))
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

Console.WriteLine($"\nTotal chunks to index: {documents.Count}");
```

</div>
</div>

### Step 4: Upload to Azure AI Search

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
# Upload documents to the search index
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)

result = search_client.upload_documents(documents)
failures = [item for item in result if not item.succeeded]
if failures:
    details = "; ".join(f"{item.key}: {item.error_message}" for item in failures)
    raise RuntimeError(f"Failed to upload search documents: {details}")

print(f"✅ Uploaded {len(result)} documents to index '{INDEX_NAME}'")
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
// Upload documents to the search index
SearchClient searchClient = new(new Uri(searchEndpoint), indexName, credential);

Response<IndexDocumentsResult> uploadResponse = await searchClient.UploadDocumentsAsync(documents);

// Validate every individual result -- a batch call can partially fail
// even when the overall request succeeds. Fail explicitly rather than
// silently dropping documents.
List<IndexingResult> failures = uploadResponse.Value.Results.Where(r => !r.Succeeded).ToList();
if (failures.Count > 0)
{
    string details = string.Join("; ", failures.Select(f => $"{f.Key}: {f.ErrorMessage}"));
    throw new InvalidOperationException($"Failed to upload search documents: {details}");
}

Console.WriteLine($"Uploaded {uploadResponse.Value.Results.Count} documents to index '{indexName}'");
```

</div>
</div>

### Step 5: Query with RAG

<div class="language-tabs" data-language-tabs markdown="1">
<div class="language-tab-panel" data-language="Python" data-language-id="python" markdown="1">
<p class="language-tab-label"><strong>Python</strong></p>

```python
from azure.search.documents.models import VectorizedQuery

def rag_query(question):
    """Full RAG pipeline: embed question → search → generate answer."""
    
    # Step 1: Embed the question
    question_embedding = get_embedding(question)
    
    # Step 2: Search the index (hybrid: keyword + vector)
    vector_query = VectorizedQuery(
        vector=question_embedding,
        k_nearest_neighbors=50,
        fields="content_vector",
    )
    
    results = search_client.search(
        search_text=question,  # keyword search
        vector_queries=[vector_query],  # vector search
        query_type="semantic",
        semantic_configuration_name="my-semantic-config",
        select=["id", "title", "category", "content"],
        top=5,
    )
    
    # Step 3: Collect retrieved context with source labels
    context_parts = []
    print("\n📚 Retrieved documents:")
    for rank, result in enumerate(results, start=1):
        source_id = f"S{rank}"
        context_parts.append(
            f"[{source_id}] Title: {result['title']}\n{result['content']}"
        )
        score = result.get("@search.reranker_score") or result["@search.score"]
        print(f"  [{source_id}] {result['title']} (score: {score:.2f})")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Step 4: Generate grounded answer
    response = openai_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "developer", "content": f"""Answer the user's question using only
            the provided context. Cite supporting sources using their labels, such as [S1].
            If the context doesn't contain the answer, say
            "I don't have enough information to answer that."
            
            Context:
            {context}"""},
            {"role": "user", "content": question},
        ],
        reasoning_effort="low",
        max_completion_tokens=800,
    )
    
    return response.choices[0].message.content

# Test it!
questions = [
    "What is Contoso's return policy?",
    "What support tiers are available?",
    "Does the warranty cover accidental damage?",
]

for q in questions:
    print(f"\n❓ Question: {q}")
    answer = rag_query(q)
    print(f"✅ Answer: {answer}")
    print("-" * 60)
```

</div>
<div class="language-tab-panel" data-language=".NET" data-language-id="dotnet" markdown="1">
<p class="language-tab-label"><strong>.NET</strong></p>

```csharp
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

    // Step 3: Collect retrieved context with source labels
    List<string> contextParts = [];
    int rank = 0;
    Console.WriteLine("\nRetrieved documents:");
    await foreach (SearchResult<SearchDocument> result in results.GetResultsAsync())
    {
        rank++;
        string sourceId = $"S{rank}";
        string title = result.Document["title"]?.ToString() ?? "";
        string content = result.Document["content"]?.ToString() ?? "";
        contextParts.Add($"[{sourceId}] Title: {title}\n{content}");

        double score = result.SemanticSearch?.RerankerScore ?? result.Score ?? 0.0;
        Console.WriteLine($"  [{sourceId}] {title} (score: {score:F2})");
    }

    string context = string.Join("\n\n---\n\n", contextParts);

    // Step 4: Generate grounded answer
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

// Test it!
string[] questions =
[
    "What is Contoso's return policy?",
    "What support tiers are available?",
    "Does the warranty cover accidental damage?",
];

foreach (string q in questions)
{
    Console.WriteLine($"\nQuestion: {q}");
    string answer = await RagQueryAsync(q);
    Console.WriteLine($"Answer: {answer}");
    Console.WriteLine(new string('-', 60));
}
```

> `KNearestNeighborsCount = 50` widens the initial vector recall set before hybrid
> and semantic reranking narrow it down to `Size = 5` -- this mirrors the Python
> `k_nearest_neighbors=50` / `top=5` pairing above.

</div>
</div>

---

## 🔍 Search Strategies Comparison

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Keyword** | Traditional text matching (BM25) | Exact terms, product names |
| **Vector** | Semantic similarity via embeddings | Natural language, synonyms |
| **Hybrid** | Both keyword + vector combined | Strong general baseline |
| **Hybrid + Semantic Ranker** | Hybrid + ML re-ranking | Higher relevance when supported |

> **Recommendation**: Start with **hybrid search plus semantic ranking**, then
> benchmark keyword, vector, hybrid, and agentic retrieval against a representative
> evaluation set. The best configuration depends on your content and query patterns.

---

## 🧪 Challenge Exercise

**Extend the RAG pipeline to:**
1. Add metadata filtering (e.g., search only within "support" documents)
2. Build a small evaluation set and measure retrieval relevance and citation correctness
3. Add follow-up question support without allowing conversation history to override retrieved facts

---

## ✅ Checkpoint

Before moving to the next lab, confirm:
- [ ] You understand the RAG pipeline (index → embed → search → generate)
- [ ] You've created an Azure AI Search index with vector fields
- [ ] You can generate embeddings and upload documents
- [ ] You can perform hybrid search and get grounded answers
- [ ] Answers reference your actual document content (not hallucinated)

---

**Next:** [Lab 5 — Prompt Engineering & Structured Outputs →](05-prompt-engineering.md)
