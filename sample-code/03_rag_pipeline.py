"""
03_rag_pipeline.py - Complete RAG Pipeline
Lab 4: Retrieval-Augmented Generation

Uses the Azure OpenAI v1 API (no dated api-version) and Microsoft Entra ID
authentication throughout -- no API keys anywhere in this script.
"""

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
from azure.search.documents.models import VectorizedQuery

load_dotenv()

# --- Configuration ---
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "hackathon-vector-index")
OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "1536"))

# Microsoft Entra ID authentication -- no API keys anywhere in this pipeline.
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

openai_client = OpenAI(
    base_url=f"{OPENAI_ENDPOINT}/openai/v1/",
    api_key=token_provider,
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)


# --- Helper Functions ---
def chunk_text(text, chunk_size_words=400, overlap_words=80):
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    step = chunk_size_words - overlap_words
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size_words])
        if chunk:
            chunks.append(chunk)
    return chunks


def get_embedding(text):
    """Generate an embedding vector for a text chunk."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


# --- Step 1: Create Search Index ---
def create_index():
    """Create the Azure AI Search index with vector and semantic search support."""
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

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

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[
            VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")
        ],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="content")],
        ),
    )
    semantic_search = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    # Fails explicitly (raises) if the service rejects the schema -- for example if
    # EMBEDDING_DIMENSIONS doesn't match the embedding deployment's actual output size.
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' created/updated")


# --- Step 2: Chunk, Embed, and Upload Documents ---
def index_documents(docs_path="data/sample-docs"):
    """Chunk, embed, and upload all documents to the search index."""
    documents = []
    doc_id = 0

    for filepath in Path(docs_path).glob("*.txt"):
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
            print(f"  Processed chunk {doc_id} from {filename}")

    result = search_client.upload_documents(documents)

    # Validate every individual result -- a batch call can partially fail even
    # when the overall request succeeds. Fail explicitly rather than silently
    # dropping documents from the index.
    failures = [item for item in result if not item.succeeded]
    if failures:
        details = "; ".join(f"{item.key}: {item.error_message}" for item in failures)
        raise RuntimeError(f"Failed to upload search documents: {details}")

    print(f"Uploaded {len(result)} chunks to index '{INDEX_NAME}'")


# --- Step 3: RAG Query ---
def rag_query(question):
    """Full RAG pipeline: embed question -> hybrid semantic search -> generate answer."""
    question_embedding = get_embedding(question)

    # Hybrid search (keyword + vector), reranked with semantic search
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

    # Collect retrieved context with source labels for citations
    context_parts = []
    print("\n  Retrieved sources:")
    for rank, result in enumerate(results, start=1):
        source_id = f"S{rank}"
        context_parts.append(f"[{source_id}] Title: {result['title']}\n{result['content']}")
        score = result.get("@search.reranker_score") or result["@search.score"]
        print(f"     [{source_id}] {result['title']} (score: {score:.2f})")

    context = "\n\n---\n\n".join(context_parts)

    # Generate a grounded answer with GPT-5.1 (a reasoning model -- no temperature)
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


# --- Main ---
if __name__ == "__main__":
    print("=" * 60)
    print("RAG Pipeline Demo")
    print("=" * 60)

    # Uncomment these for first run:
    # print("\nStep 1: Creating search index...")
    # create_index()
    # print("\nStep 2: Chunking, embedding, and indexing documents...")
    # index_documents()

    questions = [
        "What is Contoso's return policy?",
        "How much does the Contoso Watch Pro cost?",
        "My Contoso Buds won't charge. What should I do?",
        "What support tier includes phone support?",
    ]

    for q in questions:
        print(f"\n{'-' * 60}")
        print(f"Question: {q}")
        answer = rag_query(q)
        print(f"\nAnswer: {answer}")
