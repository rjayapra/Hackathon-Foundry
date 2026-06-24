---
layout: lab
title: "Lab 4: RAG"
prev_lab: /labs/03-models-and-agents
next_lab: /labs/05-prompt-engineering
---
# Lab 4: RAG — Retrieval-Augmented Generation

## 🎯 Learning Objectives

By the end of this lab, you will:
- Understand how RAG works and why it matters
- Create an Azure AI Search index with your documents
- Generate embeddings for semantic search
- Build a complete RAG pipeline that gives grounded answers

---

## What is RAG?

**RAG (Retrieval-Augmented Generation)** solves a fundamental LLM limitation: models only know what they were trained on. RAG lets you inject your own data at query time.

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

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
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
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# --- Configuration ---
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "hackathon-index")

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

# --- Step 2a: Create the Search Index ---
index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# Define index schema with vector field for embeddings
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile"
    ),
]

# Configure vector search
vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
    profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
)

# Configure semantic search (for hybrid mode)
semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(content_fields=[SemanticField(field_name="content")])
)
semantic_search = SemanticSearch(configurations=[semantic_config])

# Create the index
index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search
)

index_client.create_or_update_index(index)
print(f"✅ Index '{INDEX_NAME}' created/updated")
```

### Step 3: Chunk Documents and Generate Embeddings

```python
import glob

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_embedding(text):
    """Generate embedding for a text chunk."""
    response = openai_client.embeddings.create(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"),
        input=text
    )
    return response.data[0].embedding

# Process all documents
documents = []
doc_id = 0

for filepath in glob.glob("data/sample-docs/*.txt"):
    with open(filepath, "r") as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    chunks = chunk_text(content)
    
    for chunk in chunks:
        embedding = get_embedding(chunk)
        documents.append({
            "id": str(doc_id),
            "title": filename,
            "content": chunk,
            "content_vector": embedding
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
    credential=AzureKeyCredential(SEARCH_KEY)
)

result = search_client.upload_documents(documents)
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
        k_nearest_neighbors=3,
        fields="content_vector"
    )
    
    results = search_client.search(
        search_text=question,  # keyword search
        vector_queries=[vector_query],  # vector search
        select=["title", "content"],
        top=3
    )
    
    # Step 3: Collect retrieved context
    context_parts = []
    print("\n📚 Retrieved documents:")
    for result in results:
        context_parts.append(result["content"])
        print(f"  - {result['title']} (score: {result['@search.score']:.2f})")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Step 4: Generate grounded answer
    response = openai_client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": f"""You are a helpful assistant. Answer the user's 
            question based ONLY on the provided context. If the answer is not in the context, 
            say "I don't have enough information to answer that."
            
            Context:
            {context}"""},
            {"role": "user", "content": question}
        ],
        temperature=0.3
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
| **Hybrid** | Both keyword + vector combined | Best overall accuracy ✅ |
| **Hybrid + Semantic Ranker** | Hybrid + ML re-ranking | Production systems |

> **Recommendation**: Always use **Hybrid search** for production RAG pipelines.

---

## 🧪 Challenge Exercise

**Extend the RAG pipeline to:**
1. Add metadata filtering (e.g., search only within "support" documents)
2. Implement citation tracking — show which document chunks the answer came from
3. Add a follow-up question capability (conversation memory)

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

