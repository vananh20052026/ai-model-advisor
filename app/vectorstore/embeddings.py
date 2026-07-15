from typing import Optional
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model: Optional[SentenceTransformer] = None


class EmbeddingCache:
    """Simple in-memory cache for embeddings."""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size

    def get(self, text: str) -> Optional[list]:
        return self.cache.get(text)

    def set(self, text: str, embedding: list) -> None:
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        self.cache[text] = embedding

    def clear(self) -> None:
        self.cache.clear()


_cache = EmbeddingCache()


def get_model() -> SentenceTransformer:
    """Lazy-load embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str) -> list:
    """Embed single text with caching."""
    cached = _cache.get(text)
    if cached:
        return cached

    model = get_model()
    embedding = model.encode(text).tolist()
    _cache.set(text, embedding)

    return embedding


def embed_batch(texts: list) -> list:
    """Batch embed multiple texts."""
    model = get_model()
    return model.encode(texts).tolist()