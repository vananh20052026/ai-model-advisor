from typing import Optional
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import EMBEDDING_DIM, QDRANT_COLLECTION, QDRANT_HOST, QDRANT_PORT
from app.vectorstore.embeddings import embed_text

_client: Optional[QdrantClient] = None


def get_client() -> QdrantClient:
    """Return a cached Qdrant client, creating it on first use."""
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def ensure_collection() -> None:
    """Create the collection if it doesn't exist yet."""
    client = get_client()
    existing = {c.name for c in client.get_collections().collections}

    if QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def _make_point(chunk: dict) -> PointStruct:
    """Build a single Qdrant point from a chunk dict {'text', 'source'}."""
    return PointStruct(
        id=_new_point_id(chunk["text"]),
        vector=embed_text(chunk["text"]),
        payload={"text": chunk["text"], "source": chunk["source"]},
    )


def _new_point_id(text: str) -> int:
    """Generate deterministic id from content hash (avoids duplicates)."""
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)


def upsert_chunks(chunks: list[dict]) -> int:
    """
    Insert or update a list of chunks into the vector store.

    Each chunk must be a dict with keys: 'text', 'source'.
    Returns the number of chunks written.
    """
    if not chunks:
        return 0

    ensure_collection()
    client = get_client()
    points = [_make_point(chunk) for chunk in chunks]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    return len(points)


def search(query: str, top_k: int = 3) -> list[dict]:
    """
    Find the top_k chunks most semantically similar to the query.

    Returns a list of dicts: {'text', 'source', 'score'}.
    """
    ensure_collection()
    client = get_client()

    response = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=embed_text(query),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": hit.payload["text"],
            "source": hit.payload["source"],
            "score": round(hit.score, 4),
        }
        for hit in response.points
    ]