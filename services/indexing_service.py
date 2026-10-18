import os

from config import fetch_courses
from services.chunking_service import chunk_text
from services.embedding_service import embed_chunks
from services.vector_store import add_chunks, clear_collection


def read_text_file(file_path):
    """
    Read a text file, trying several encodings.
    latin-1 accepts any byte, so it works as a last resort.
    Returns (text, encoding) or (None, None) if reading fails.
    """

    for encoding in ("utf-8", "Windows-1252", "latin-1"):

        try:

            with open(file_path, "r", encoding=encoding) as file:
                return file.read(), encoding

        except UnicodeDecodeError:
            continue

        except OSError as error:
            print(f"❌ Could not open {file_path}: {error}")
            return None, None

    return None, None


def build_course_index():

    print("\n" + "=" * 70)
    print("BUILDING COURSE + DOCUMENT INDEX")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Fetch courses from MySQL
    # ---------------------------------------------------------

    courses = fetch_courses()

    if not courses:
        print("❌ No courses found in database.")
        return

    print(f"\nFound {len(courses)} courses.")

    # ---------------------------------------------------------
    # 2. Clear old ChromaDB collection
    # ---------------------------------------------------------

    print("\nClearing old ChromaDB collection...")
    clear_collection()

    # ---------------------------------------------------------
    # 3. Prepare storage for all chunks
    # ---------------------------------------------------------

    all_chunks = []
    all_metadata = []

    # ---------------------------------------------------------
    # 4. Index MySQL course descriptions
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("INDEXING MYSQL COURSES")
    print("=" * 70)

    for course in courses:

        text = f"""
Course Name: {course['course_name']}

Trainer: {course['trainer']}

Price: {course['course_price']}

Duration: {course['duration']}

Description:
{course['course_description']}
"""

        chunks = chunk_text(text)

        print("\n" + "-" * 70)
        print("MYSQL COURSE:", course["course_name"])
        print("Course ID:", course["id"])
        print("Chunks:", len(chunks))
        print("-" * 70)

        for chunk in chunks:

            all_chunks.append(chunk)

            all_metadata.append({
                "course_id": str(course["id"]),
                "course_name": course["course_name"],
                "trainer": course["trainer"],
                "duration": str(course["duration"]),
                "price": float(course["course_price"]),
                "source": "course_description"
            })

    # ---------------------------------------------------------
    # 5. Locate all .txt documents in rag_documents/
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("INDEXING RAG DOCUMENTS")
    print("=" * 70)

    # Project root directory:
    # Chatbot2/
    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    documents_dir = os.path.join(BASE_DIR, "rag_documents")

    print("Documents folder:")
    print(documents_dir)

    if not os.path.isdir(documents_dir):

        print("\n❌ rag_documents folder NOT FOUND!")
        txt_files = []

    else:

        txt_files = sorted(
            file_name
            for file_name in os.listdir(documents_dir)
            if file_name.lower().endswith(".txt")
        )

    print("Text files found:", len(txt_files))

    for file_name in txt_files:
        print("  -", file_name)

    if not txt_files:
        print("\n⚠️ No documents to index. Only courses will be indexed.")

    # ---------------------------------------------------------
    # 6. Read + chunk each document
    # ---------------------------------------------------------

    documents_indexed = 0

    for file_name in txt_files:

        file_path = os.path.join(documents_dir, file_name)

        print("\n" + "-" * 70)
        print("DOCUMENT:", file_name)
        print("-" * 70)

        document_text, encoding = read_text_file(file_path)

        if document_text is None or not document_text.strip():
            print("⚠️ Skipping empty or unreadable file.")
            continue

        print("Encoding:", encoding)
        print("Characters:", len(document_text))

        document_chunks = chunk_text(document_text)

        print("Chunks:", len(document_chunks))

        if not document_chunks:
            print("⚠️ No chunks created. Skipping file.")
            continue

        # Readable title from file name:
        # "hci(2025).txt" -> "hci(2025)"
        document_title = os.path.splitext(file_name)[0]

        # ---------------------------------------------------------
        # 7. Add document chunks + metadata
        # ---------------------------------------------------------

        for chunk in document_chunks:

            all_chunks.append(chunk)

            all_metadata.append({
                "course_id": "rag_document",
                "course_name": document_title,
                "trainer": "N/A",
                "duration": "N/A",
                "price": 0.0,
                "source": "rag_document",
                "file_name": file_name,
                "document_type": "book"
            })

        documents_indexed += 1

    print(f"\nDocuments indexed: {documents_indexed}/{len(txt_files)}")

    # ---------------------------------------------------------
    # 8. Check total chunks
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("INDEXING SUMMARY")
    print("=" * 70)

    print("Total chunks:", len(all_chunks))
    print("Total metadata:", len(all_metadata))

    if not all_chunks:

        print("\n❌ No chunks available for indexing.")
        return

    if len(all_chunks) != len(all_metadata):

        print("\n❌ ERROR:")
        print("Number of chunks and metadata entries do not match.")

        print("Chunks:", len(all_chunks))
        print("Metadata:", len(all_metadata))

        return

    # ---------------------------------------------------------
    # 9. Create embeddings
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("CREATING EMBEDDINGS")
    print("=" * 70)

    try:

        embeddings = embed_chunks(all_chunks)

        print("✅ Embeddings created successfully.")

        print(
            "Embedding count:",
            len(embeddings)
        )

    except Exception as error:

        print("\n❌ Error while creating embeddings:")
        print(error)

        return

    # ---------------------------------------------------------
    # 10. Add everything to ChromaDB
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("ADDING DATA TO CHROMADB")
    print("=" * 70)

    try:

        add_chunks(
            all_chunks,
            embeddings,
            all_metadata
        )

        print("\n✅ All chunks added to ChromaDB successfully.")

    except Exception as error:

        print("\n❌ Error while adding chunks to ChromaDB:")
        print(error)

        return

    # ---------------------------------------------------------
    # 11. Final summary
    # ---------------------------------------------------------

    document_count = sum(
        1
        for metadata in all_metadata
        if metadata.get("source") == "rag_document"
    )

    course_count = sum(
        1
        for metadata in all_metadata
        if metadata.get("source") == "course_description"
    )

    print("\n" + "=" * 70)
    print("INDEXING COMPLETED")
    print("=" * 70)

    print("Course chunks:", course_count)
    print("Document chunks:", document_count)
    print("Total chunks:", len(all_chunks))

    # Per-file breakdown
    file_counts = {}

    for metadata in all_metadata:

        if metadata.get("source") == "rag_document":

            name = metadata["file_name"]
            file_counts[name] = file_counts.get(name, 0) + 1

    for name, count in file_counts.items():
        print(f"  {name}: {count} chunks")

    print("\n✅ Index built successfully.")
    print("=" * 70)


# -------------------------------------------------------------
# Run this file directly with:
#
# python -m services.indexing_service
# -------------------------------------------------------------

if __name__ == "__main__":
    build_course_index()