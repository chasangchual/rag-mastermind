## Create the Qdrant Collection

This application uses Qdrant to store and search document chunk embeddings for the RAG pipeline.

The recommended configuration is:

| Setting                | Value                 |
| ---------------------- | --------------------- |
| Collection name        | `rag_document_chunks` |
| Search scope           | Global Search         |
| Search type            | Simple Hybrid Search  |
| Dense vector name      | `dense`               |
| Dense vector dimension | `4096`                |
| Distance metric        | Cosine                |
| Sparse vector name     | `sparse`              |

Hybrid search combines:

* Dense vector search for semantic similarity
* Sparse vector search for exact words, identifiers, names, dates, and technical terminology

### Create the Collection Using the Qdrant Web UI

Open the Qdrant dashboard:

```text
http://localhost:6333/dashboard
```

Select **Collections**, and then select **Create collection**.

Configure the collection as follows.

#### 1. Collection name

```text
rag_document_chunks
```

#### 2. Search scope

Select:

```text
Global Search
```

Global Search creates an index across the complete collection. Queries can still be restricted using metadata filters such as:

```text
tenant_id
knowledge_base_id
document_id
is_archived
```

Do not select the specialized Multitenancy option unless every query is always restricted to a specific tenant.

#### 3. Search configuration

Select:

```text
Simple Hybrid Search
```

This creates one dense vector and one sparse vector for each document chunk.

#### 4. Dense vector configuration

Use the following values:

```text
Vector name: dense
Dimension:   4096
Distance:    Cosine
```

The dimension must exactly match the embedding model output dimension.

For example, an embedding model that returns 4,096 values requires:

```text
Dimension: 4096
```

Do not change the embedding model dimension after documents have already been indexed. A different embedding dimension requires a new collection or complete reindexing.

#### 5. Sparse vector configuration

Use:

```text
Sparse vector name: sparse
```

The sparse vector is used for lexical search, such as matching:

* Document numbers
* Policy identifiers
* Error codes
* Names
* Dates
* Acronyms
* Exact Korean or English terminology

After reviewing the settings, select **Create Collection**.

### Recommended Point Structure

Each Qdrant point represents one document chunk.

```json
{
  "id": "8e217b44-465a-4ae4-bcce-a41167430e78",
  "vector": {
    "dense": [0.0123, -0.0456, 0.0789],
    "sparse": {
      "indices": [12, 184, 991],
      "values": [0.72, 0.41, 0.93]
    }
  },
  "payload": {
    "tenant_id": "tenant-001",
    "knowledge_base_id": "kb-001",
    "document_id": "document-001",
    "filename": "employee-policy.pdf",
    "document_type": "pdf",
    "page_number": 12,
    "chunk_index": 4,
    "is_archived": false,
    "text": "The original text extracted from the document chunk.",
    "embedding_model": "embedding-model-name",
    "embedding_dimension": 4096,
    "embedding_version": "v1"
  }
}
```

The abbreviated dense vector above is only an example. The actual `dense` vector must contain exactly 4,096 values.

### Recommended Payload Indexes

Create payload indexes for fields frequently used in filters.

Recommended fields:

| Field               | Type    | Purpose                                       |
| ------------------- | ------- | --------------------------------------------- |
| `tenant_id`         | Keyword | Restrict results to an organization           |
| `knowledge_base_id` | Keyword | Search selected knowledge bases               |
| `document_id`       | Keyword | Find or delete chunks belonging to a document |
| `document_type`     | Keyword | Filter by PDF, Word, HTML, or other type      |
| `is_archived`       | Boolean | Exclude archived documents                    |
| `page_number`       | Integer | Filter or inspect document pages              |

Payload indexes can be created through the Qdrant API.

```bash
curl -X PUT \
  "http://localhost:6333/collections/rag_document_chunks/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "tenant_id",
    "field_schema": "keyword"
  }'
```

Create the remaining indexes similarly:

```bash
curl -X PUT \
  "http://localhost:6333/collections/rag_document_chunks/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "knowledge_base_id",
    "field_schema": "keyword"
  }'

curl -X PUT \
  "http://localhost:6333/collections/rag_document_chunks/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "document_id",
    "field_schema": "keyword"
  }'

curl -X PUT \
  "http://localhost:6333/collections/rag_document_chunks/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "document_type",
    "field_schema": "keyword"
  }'

curl -X PUT \
  "http://localhost:6333/collections/rag_document_chunks/index" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "is_archived",
    "field_schema": "bool"
  }'
```

When Qdrant API-key authentication is enabled, include the API key:

```bash
-H "api-key: ${QDRANT_API_KEY}"
```

### Create the Collection Programmatically

The collection can also be created using the Qdrant Python client.

Install the client:

```bash
pip install qdrant-client
```

Create the collection:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    SparseVectorParams,
    VectorParams,
)

COLLECTION_NAME = "rag_document_chunks"
VECTOR_DIMENSION = 4096

client = QdrantClient(
    url="http://localhost:6333",
    api_key=None,
)

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(
                size=VECTOR_DIMENSION,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams()
        },
    )

payload_indexes = {
    "tenant_id": PayloadSchemaType.KEYWORD,
    "knowledge_base_id": PayloadSchemaType.KEYWORD,
    "document_id": PayloadSchemaType.KEYWORD,
    "document_type": PayloadSchemaType.KEYWORD,
    "is_archived": PayloadSchemaType.BOOL,
    "page_number": PayloadSchemaType.INTEGER,
}

for field_name, field_schema in payload_indexes.items():
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name=field_name,
        field_schema=field_schema,
    )
```

When an API key is configured:

```python
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
```

### Environment Variables

Add the following values to `.env`:

```dotenv
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=replace-with-a-secure-api-key
QDRANT_COLLECTION_NAME=rag_document_chunks
QDRANT_DENSE_VECTOR_NAME=dense
QDRANT_SPARSE_VECTOR_NAME=sparse
EMBEDDING_DIMENSION=4096
```

The application must use the same vector names configured in the collection:

```text
dense
sparse
```

A mismatch such as `embedding`, `default`, or `text_vector` will cause Qdrant queries or insert operations to fail.

### Verify the Collection

Check the collection configuration:

```bash
curl \
  "http://localhost:6333/collections/rag_document_chunks"
```

With API-key authentication:

```bash
curl \
  -H "api-key: ${QDRANT_API_KEY}" \
  "http://localhost:6333/collections/rag_document_chunks"
```

The response should show:

```text
dense vector size: 4096
dense distance: Cosine
sparse vector: sparse
collection status: green
```

You can also verify it in the Qdrant dashboard:

```text
http://localhost:6333/dashboard#/collections/rag_document_chunks
```

### Retrieval Strategy

The recommended implementation sequence is:

#### Phase 1: Dense retrieval

Start with the 4,096-dimensional dense vector.

```text
User query
    ↓
Dense embedding
    ↓
Qdrant semantic search
    ↓
Top document chunks
```

#### Phase 2: Hybrid retrieval

Add sparse retrieval for exact lexical matches.

```text
User query
    ├── Dense embedding search
    └── Sparse keyword search
              ↓
        Rank fusion
              ↓
       Top document chunks
```

Hybrid search is particularly useful for PDF documents containing exact identifiers, policy numbers, dates, product names, or Korean and English technical terminology.

### Important Constraints

* A dense vector must contain exactly 4,096 values.
* Documents and queries must use the same embedding model.
* Dense and sparse vectors must use the configured names: `dense` and `sparse`.
* Changing the embedding model normally requires re-embedding all document chunks.
* Always apply `tenant_id` or access-control filters before returning search results.
* Store the embedding model name and version in the payload or document metadata.
* Do not expose the Qdrant API port directly to the public internet without authentication and network restrictions.
