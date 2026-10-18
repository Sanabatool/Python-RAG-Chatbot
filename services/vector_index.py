from services.chunking_service import chunk_text
from services.embedding_service import embed_chunks


class VectorIndex:

    def __init__(self):
        self.index = []

    def build(self, courses):
        """
        Build embeddings for all course chunks.
        """

        self.index = []

        chunk_id = 0

        for course in courses:

            document = f"""
Course Name: {course['course_name']}
Trainer: {course['trainer']}
Price: {course['course_price']}
Duration: {course['duration']}
Description:
{course['course_description']}
"""

            chunks = chunk_text(document)

            embeddings = embed_chunks(chunks)

            for chunk, embedding in zip(chunks, embeddings):

                self.index.append({

                    "chunk_id": chunk_id,

                    "course_id": course["id"],

                    "course_name": course["course_name"],

                    "text": chunk,

                    "embedding": embedding

                })

                chunk_id += 1

    def get_index(self):
        return self.index


vector_index = VectorIndex()