This is your current pipeline.

build_index.py
        │
        ▼
indexing_service.py
        │
        ▼
chunking_service.py
        │
        ▼
embedding_service.py
        │
        ▼
vector_store.py
        │
        ▼
ChromaDB

Later...

User asks question

↓

router.py

↓

rag_service.py

↓

retrieval_service.py

↓

embedding_service.py

↓

vector_store.py

↓

ChromaDB

↓

Top chunks

↓

rag_service.py

↓

LLM

↓

Answer

