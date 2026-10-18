# ============================================================
# RETRIEVAL SERVICE
# ============================================================
# Responsibilities:
# 1. Convert question into embedding
# 2. Apply metadata filter (explicit, or auto-detected)
# 3. Search ChromaDB
# 4. Check relevance
# 5. Return ranked relevant chunks
# ============================================================

from services.embedding_service import embed_text
from services.vector_store import search
from services.metadata_service import detect_metadata


# Lower cosine distance = more similar
# Start conservatively and tune during evaluation.
RELEVANCE_THRESHOLD = 0.90


def retrieve_context(question, k=5, where=None):
    """
    question -> text to embed and search with
    k        -> number of chunks to retrieve
    where    -> optional explicit metadata filter, e.g.
                {"source": "rag_document"} to search book chunks only.
                If given, automatic metadata detection is skipped so
                a detected course filter can't conflict with it.
    """

    print("\n========== RETRIEVAL ==========")
    print("Question:", question)

    # ------------------------------------------------------------
    # 1. CREATE QUERY EMBEDDING
    # ------------------------------------------------------------

    query_embedding = embed_text(question)

    # ------------------------------------------------------------
    # 2. CHOOSE METADATA FILTER
    # ------------------------------------------------------------

    if where:
        metadata_filter = where
        print("Metadata (explicit):", metadata_filter)
    else:
        metadata_filter = detect_metadata(question)
        print("Metadata (detected):", metadata_filter)

    # ------------------------------------------------------------
    # 3. SEARCH CHROMADB
    # ------------------------------------------------------------

    results = search(
        query_embedding,
        k=k,
        where=metadata_filter if metadata_filter else None
    )

    # ------------------------------------------------------------
    # 4. SAFELY READ RESULTS
    # ------------------------------------------------------------

    documents = results.get("documents", [[]])
    distances = results.get("distances", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:

        print("No documents retrieved.")

        return []

    documents = documents[0]

    distances = (
        distances[0]
        if distances
        else []
    )

    metadatas = (
        metadatas[0]
        if metadatas
        else []
    )

    # ------------------------------------------------------------
    # 5. BUILD RETRIEVED CHUNKS
    # ------------------------------------------------------------

    retrieved = []

    for index, document in enumerate(documents):

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        # --------------------------------------------------------
        # RELEVANCE FILTER
        # --------------------------------------------------------

        if distance is not None and distance > RELEVANCE_THRESHOLD:

            print(
                f"Rejected chunk {index + 1} "
                f"(distance={distance:.4f})"
            )

            continue

        retrieved.append(
            {
                "text": document,
                "score": distance,      # kept for existing code
                "distance": distance,   # used by rag_service
                "metadata": metadata
            }
        )

    # ------------------------------------------------------------
    # 6. NO RELEVANT RESULTS
    # ------------------------------------------------------------

    if not retrieved:

        print(
            "\nNo chunks passed the relevance threshold."
        )

        return []

    # ------------------------------------------------------------
    # 7. DEBUG OUTPUT
    # ------------------------------------------------------------

    print("\n===== RELEVANT CHUNKS =====")

    for i, chunk in enumerate(retrieved, start=1):

        print(f"\nChunk {i}")
        print("Text:", chunk["text"][:300])
        print("Metadata:", chunk["metadata"])
        print("Distance:", chunk["distance"])
        print("----------------")

    print(
        f"\nRetrieved {len(retrieved)} relevant chunks."
    )

    return retrieved