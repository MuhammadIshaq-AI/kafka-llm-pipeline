from pinecone import Pinecone
from src.utils.config import Config

class PineconeManager:
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)

    def upsert_vectors(self, vectors: list[dict]):
        """
        Upsert vectors to Pinecone.
        Format: [{"id": "doc1_chunk1", "values": [0.1, 0.2...], "metadata": {"text": "chunk text"}}]
        """
        self.index.upsert(vectors=vectors)

    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """Query Pinecone for similar vectors."""
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return response.get("matches", [])
