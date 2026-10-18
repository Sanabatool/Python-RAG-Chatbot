from sentence_transformers import SentenceTransformer


# Load the model only once.
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def embed_text(text):
    """
    Convert one piece of text into a vector.
    """

    return model.encode(
        text,
        normalize_embeddings=True
    )


def embed_chunks(chunks):
    """
    Convert multiple text chunks into vectors.
    """

    return model.encode(
        chunks,
        normalize_embeddings=True
    )