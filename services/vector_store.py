# ============================================================
# VECTOR STORE
# ============================================================
# This file ONLY communicates with ChromaDB.
#
# Responsibilities:
# 1. Create/connect to ChromaDB
# 2. Store course chunks + embeddings + metadata
# 3. Search vectors
# 4. Clear/rebuild the collection
# ============================================================

# ============================================================
# VECTOR STORE
# ============================================================

import os
from chromadb import PersistentClient


# ============================================================
# CHROMADB PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

VECTOR_DB_PATH = os.path.join(
    BASE_DIR,
    "vector_db"
)

print("ChromaDB path:", VECTOR_DB_PATH)


# ============================================================
# CHROMADB CLIENT
# ============================================================

client = PersistentClient(
    path=VECTOR_DB_PATH
)


# ============================================================
# COLLECTION
# ============================================================

collection = client.get_or_create_collection(
    name="courses",
    metadata={
        "hnsw:space": "cosine"
    }
)


# ============================================================
# ADD / STORE CHUNKS
# ============================================================

def add_chunks(chunks, embeddings, metadatas, batch_size=1000):
    """
    Store chunks, embeddings, and metadata in ChromaDB,
    in batches to stay under ChromaDB's max batch size.
    """

    if not chunks:
        print("No chunks to add.")
        return

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must be the same."
        )

    if len(chunks) != len(metadatas):
        raise ValueError(
            "Number of chunks and metadata entries must be the same."
        )

    # Works for both numpy arrays and plain lists
    if hasattr(embeddings, "tolist"):
        embeddings = embeddings.tolist()

    start_id = collection.count()

    for start in range(0, len(chunks), batch_size):

        end = start + batch_size

        collection.add(
            ids=[
                f"chunk_{start_id + i}"
                for i in range(start, min(end, len(chunks)))
            ],
            documents=chunks[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end]
        )

        print(
            f"Added {min(end, len(chunks))}/{len(chunks)} chunks..."
        )

    print(f"Added {len(chunks)} chunks to ChromaDB.")

# ============================================================
# SEARCH
# ============================================================

def search(query_embedding, k=3, where=None):
    """
    Search ChromaDB using vector similarity.

    query_embedding -> embedding of user's question
    k               -> number of results
    where           -> optional metadata filter
    """

    # --------------------------------------------------------
    # Check whether collection contains data
    # --------------------------------------------------------

    total_documents = collection.count()


    if total_documents == 0:

        print(
            "ChromaDB collection is empty."
        )

        return {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]]
        }


    # --------------------------------------------------------
    # Don't request more documents than available
    # --------------------------------------------------------

    k = min(k, total_documents)


    # --------------------------------------------------------
    # Search WITH metadata filter
    # --------------------------------------------------------

    if where:

        print(
            "Searching WITH metadata:",
            where
        )

        results = collection.query(

            query_embeddings=[
                query_embedding.tolist()
            ],

            n_results=k,

            where=where

        )


    # --------------------------------------------------------
    # Search WITHOUT metadata filter
    # --------------------------------------------------------

    else:

        print(
            "Searching WITHOUT metadata..."
        )

        results = collection.query(

            query_embeddings=[
                query_embedding.tolist()
            ],

            n_results=k

        )


    return results


# ============================================================
# CLEAR COLLECTION
# ============================================================

def clear_collection():
    """
    Delete all existing course vectors and create
    a fresh empty collection.

    Useful when rebuilding the complete course index.
    """

    global collection


    try:

        client.delete_collection(
            name="courses"
        )

        print(
            "Old ChromaDB collection deleted."
        )

    except Exception:

        print(
            "No existing collection to delete."
        )


    # --------------------------------------------------------
    # Create fresh collection
    # --------------------------------------------------------

    collection = client.get_or_create_collection(

        name="courses",

        metadata={
            "hnsw:space": "cosine"
        }

    )


    print(
        "ChromaDB collection cleared successfully."
    )