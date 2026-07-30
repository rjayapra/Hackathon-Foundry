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

### 🐍 Option B: Build RAG with Python (Code-First)

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

```powershell
pip install --upgrade openai azure-identity azure-search-documents python-dotenv
az login
```

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

> `text-embedding-3-small` produces up to 1,536 dimensions and
> `text-embedding-3-large` produces up to 3,072. The index field dimension must
> exactly match the dimension returned by your embedding deployment.

### Step 3: Chunk Documents and Generate Embeddings

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

### Step 4: Upload to Azure AI Search

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

### Step 5: Query with RAG

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
