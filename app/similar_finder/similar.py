"""
Similar Laptop Finder.

Finds laptops with similar specifications using vector embeddings (FAISS)
rather than naive rule-based filtering — two laptops with different exact
specs but similar overall positioning (e.g. both "lightweight business
ultrabooks") will be found as similar.
"""
from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.search import semantic_search
from app.models.db_models import Laptop


def find_similar_laptops(db: Session, laptop_id: int, top_k: int = 6) -> List[Tuple[Laptop, float]]:
    similar_ids_scores = semantic_search.find_similar(laptop_id, top_k=top_k)
    id_to_score = dict(similar_ids_scores)
    laptops = db.query(Laptop).filter(Laptop.id.in_(id_to_score.keys())).all()
    laptops.sort(key=lambda lp: id_to_score[lp.id], reverse=True)
    return [(lp, id_to_score[lp.id]) for lp in laptops]
