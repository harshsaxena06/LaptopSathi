"""
Semantic Search Engine.

Encodes laptop `description_text` into dense vectors with Sentence
Transformers, indexes them with FAISS (cosine similarity via inner product
on normalized vectors), and answers natural-language queries like:
  "I need a lightweight laptop for AI under 90000"
  "Best laptop for Android development"
  "Gaming laptop with excellent battery"

This is a singleton-style module: build_index() is run once by
scripts/build_embeddings.py (or on startup if no index exists), and the
FastAPI app calls `search()` at request time, which just loads the model +
index once and reuses them.
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.models.db_models import Laptop, EmbeddingMetadata
from app.utils.exceptions import DependencyNotReadyError, InvalidRequestError

logger = logging.getLogger("laptopsathi.search")

_model = None
_index = None
_id_map: list[int] = []  # faiss row position -> laptop.id


def _get_model():
    """Lazy-load the sentence-transformers model (heavy import, load once)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model %s", settings.EMBEDDING_MODEL_NAME)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_index(db: Session) -> int:
    """
    (Re)builds the FAISS index from every active laptop's description_text.
    Persists the index to disk and records embedding metadata in the DB so
    stale embeddings can be detected on future partial updates.
    """
    import faiss

    model = _get_model()
    laptops: List[Laptop] = db.query(Laptop).filter(Laptop.is_active.is_(True)).all()
    if not laptops:
        logger.warning("No laptops found to index.")
        return 0

    texts = [lp.description_text or f"{lp.brand.name} {lp.model_name}" for lp in laptops]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine similarity
    index.add(embeddings)

    settings.FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(settings.FAISS_INDEX_PATH))

    # Persist row -> laptop_id mapping + embedding metadata
    id_map_path = settings.EMBEDDINGS_DIR / "id_map.npy"
    np.save(id_map_path, np.array([lp.id for lp in laptops]))

    for pos, (lp, text) in enumerate(zip(laptops, texts)):
        meta = db.query(EmbeddingMetadata).filter_by(laptop_id=lp.id).one_or_none()
        h = _text_hash(text)
        if meta is None:
            meta = EmbeddingMetadata(
                laptop_id=lp.id, faiss_index_position=pos,
                embedding_model=settings.EMBEDDING_MODEL_NAME, text_hash=h,
            )
            db.add(meta)
        else:
            meta.faiss_index_position = pos
            meta.embedding_model = settings.EMBEDDING_MODEL_NAME
            meta.text_hash = h
    db.commit()

    global _index, _id_map
    _index = index
    _id_map = [lp.id for lp in laptops]

    logger.info("FAISS index built with %d vectors (dim=%d)", index.ntotal, dim)
    return index.ntotal


def _load_index_if_needed():
    global _index, _id_map
    if _index is not None:
        return
    import faiss
    if not settings.FAISS_INDEX_PATH.exists():
        raise DependencyNotReadyError(
            "Semantic search index not found. Run `python scripts/build_embeddings.py` first."
        )
    _index = faiss.read_index(str(settings.FAISS_INDEX_PATH))
    id_map_path = settings.EMBEDDINGS_DIR / "id_map.npy"
    _id_map = np.load(id_map_path).tolist()


def search(query: str, top_k: int = 10) -> List[Tuple[int, float]]:
    """Returns a list of (laptop_id, similarity_score) sorted by descending similarity."""
    _load_index_if_needed()
    model = _get_model()

    query_vec = model.encode([query], convert_to_numpy=True)
    import faiss
    faiss.normalize_L2(query_vec)

    scores, positions = _index.search(query_vec, min(top_k, _index.ntotal))
    results = []
    for score, pos in zip(scores[0], positions[0]):
        if pos == -1:
            continue
        laptop_id = _id_map[pos]
        results.append((int(laptop_id), float(score)))
    return results


def find_similar(laptop_id: int, top_k: int = 6) -> List[Tuple[int, float]]:
    """Similar-laptop finder: search using the target laptop's own embedding position."""
    _load_index_if_needed()
    if laptop_id not in _id_map:
        raise InvalidRequestError(f"Laptop {laptop_id} has no embedding. Rebuild the index.")
    pos = _id_map.index(laptop_id)
    vec = _index.reconstruct(pos).reshape(1, -1)
    scores, positions = _index.search(vec, min(top_k + 1, _index.ntotal))
    results = []
    for score, p in zip(scores[0], positions[0]):
        lid = _id_map[p]
        if lid == laptop_id:
            continue  # exclude itself
        results.append((int(lid), float(score)))
    return results[:top_k]
