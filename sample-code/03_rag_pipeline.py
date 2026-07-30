"""
03_rag_pipeline.py - Complete RAG Pipeline
Lab 4: Retrieval-Augmented Generation
"""

import os
import glob
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
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# ─── Configuration ───────────────────────────────────────────────
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "hackathon-index")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1")
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)


# ─── Helper Functions ────────────────────────────────────────────
def chunk_text(text, chunk_size=300, overlap=50):
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def get_embedding(text):
    """Generate embedding vector for text."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding


# ─── Step 1: Create Search Index ────────────────────────────────
def create_index():
    """Create Azure AI Search index with vector support."""
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

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

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )
    semantic_search = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )

    index_client.create_or_update_index(index)
    print(f"✅ Index '{INDEX_NAME}' created/updated")


# ─── Step 2: Index Documents ────────────────────────────────────
def index_documents(docs_path="data/sample-docs"):
    """Process and upload documents to the search index."""
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    documents = []
    doc_id = 0

    for filepath in glob.glob(f"{docs_path}/*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
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
            print(f"  📄 Chunk {doc_id}: {filename}")

    result = search_client.upload_documents(documents)
    print(f"\n✅ Uploaded {len(result)} chunks to index '{INDEX_NAME}'")


# ─── Step 3: RAG Query ──────────────────────────────────────────
def rag_query(question):
    """Execute full RAG pipeline: embed → search → generate."""
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    # Embed the question
    question_embedding = get_embedding(question)

    # Hybrid search (keyword + vector)
    vector_query = VectorizedQuery(
        vector=question_embedding,
        k_nearest_neighbors=3,
        fields="content_vector"
    )

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=["title", "content"],
        top=3
    )

    # Collect context
    context_parts = []
    print("\n  📚 Retrieved sources:")
    for result in results:
        context_parts.append(result["content"])
        print(f"     - {result['title']} (score: {result['@search.score']:.3f})")

    context = "\n\n---\n\n".join(context_parts)

    # Generate grounded answer
    response = openai_client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": f"""Answer the user's question based ONLY on this context.
            If the answer isn't in the context, say "I don't have that information."
            Cite the source document when possible.

            Context:
            {context}"""},
            {"role": "user", "content": question}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# ─── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 RAG Pipeline Demo")
    print("=" * 60)

    # Uncomment these for first run:
    # print("\n📦 Step 1: Creating search index...")
    # create_index()
    # print("\n📄 Step 2: Indexing documents...")
    # index_documents()

    # Query
    questions = [
        "What is Contoso's return policy?",
        "How much does the Contoso Watch Pro cost?",
        "My Contoso Buds won't charge. What should I do?",
        "What support tier includes phone support?",
    ]

    for q in questions:
        print(f"\n{'─'*60}")
        print(f"❓ {q}")
        answer = rag_query(q)
        print(f"\n✅ {answer}")
