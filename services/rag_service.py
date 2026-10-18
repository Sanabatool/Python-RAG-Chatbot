from services.retrieval_service import retrieve_context
from services.llm_service import ask_llm


NO_ANSWER = (
    "I couldn't find that information in the available course material."
)

# Chunks farther than this are treated as unrelated (lower = stricter).
# Start here and tune it by watching the "Distance:" values in your logs.
MAX_DISTANCE = 0.55

# Ignore tiny chunks such as single bibliography lines
MIN_CHUNK_CHARS = 80


def ask_rag(question, search_question=None, source=None):
    """
    question        -> the user's original question (shown to the LLM)
    search_question -> rewritten standalone query used for retrieval
                       (e.g. "its types from book" -> "machine learning types")
    source          -> optional metadata filter, e.g. "rag_document"
                       to search only book/document chunks
    """

    print("\n========== RAG ==========")
    print("Question:", question)

    query = search_question or question

    print("Search query:", query)
    print("Source filter:", source)

    # ------------------------------------------------------------
    # 1. RETRIEVE RELEVANT CHUNKS
    # ------------------------------------------------------------

    where = {"source": source} if source else None

    chunks = retrieve_context(
        query,
        k=5,
        where=where
    )

    if not chunks:

        print("No relevant chunks found.")

        return NO_ANSWER

    # ------------------------------------------------------------
    # 2. FILTER WEAK / TINY CHUNKS
    # ------------------------------------------------------------

    good_chunks = []

    for chunk in chunks:

        text = chunk.get("text", "").strip()
        distance = chunk.get("distance")

        if len(text) < MIN_CHUNK_CHARS:
            print("Skipping tiny chunk:", text[:40])
            continue

        if distance is not None and distance > MAX_DISTANCE:
            print(f"Skipping weak chunk (distance {distance:.3f})")
            continue

        good_chunks.append(chunk)

    if not good_chunks:

        print("No chunks passed the relevance filter.")

        return NO_ANSWER

    # ------------------------------------------------------------
    # 3. BUILD CONTEXT
    # ------------------------------------------------------------

    context_parts = []

    for i, chunk in enumerate(good_chunks, start=1):

        metadata = chunk.get("metadata", {})

        chunk_source = metadata.get("source", "Unknown source")
        name = metadata.get("course_name", "Unknown")
        text = chunk.get("text", "").strip()

        if chunk_source == "rag_document":
            label = f"Book/Document: {name}"
        else:
            label = f"Course: {name}"

        context_parts.append(
            f"""
SOURCE {i}

{label}

Content:
{text}

---
"""
        )

    context = "\n".join(context_parts)

    # ------------------------------------------------------------
    # 4. BUILD RAG PROMPT
    # ------------------------------------------------------------

    interpreted_line = ""

    if search_question and search_question.strip().lower() != question.strip().lower():
        interpreted_line = f"\nThe question refers to this topic: {search_question}\n"

    prompt = f"""
You are an AI Learning Assistant for an online learning platform.

Answer the user's question using ONLY the retrieved material
provided below.

IMPORTANT RULES:

1. The retrieved material is your only source of truth.

2. Do NOT invent or assume information.

3. Do NOT use outside knowledge to fill missing information.

4. If the user's question is not answered by the retrieved
   material, respond exactly with:

   "I couldn't find that information in the available course material."

5. Ignore retrieved text that is unrelated to the question, such
   as reference lists, ISBN numbers, or citations.

6. If the material comes from more than one book or course,
   clearly say which one each part of the answer comes from.

7. Do not mention retrieval distance, embeddings, ChromaDB,
   vector databases, RAG, or other technical implementation
   details.

8. Keep the answer concise and useful.

RETRIEVED MATERIAL:

{context}

USER QUESTION:

{question}
{interpreted_line}
ANSWER:
"""

    print("\n========== RAG PROMPT ==========")
    print(prompt)
    print("\n=================================")

    # ------------------------------------------------------------
    # 5. GENERATE ANSWER
    # ------------------------------------------------------------

    answer = ask_llm(prompt)

    if not answer:
        return NO_ANSWER

    return answer.strip()