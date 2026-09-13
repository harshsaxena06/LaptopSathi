from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Laptop, User
from app.schemas.schemas import SearchQuery, SearchResponse, SearchResultItem
from app.search import semantic_search
from app.utils.serializers import laptop_to_out
from app.personalization import user_engine
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])


@router.post("", response_model=SearchResponse)
def semantic_search_endpoint(
    payload: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # semantic_search.search raises DependencyNotReadyError (-> HTTP 503) if the
    # FAISS index hasn't been built yet; handled centrally in app.main.
    raw_results = semantic_search.search(payload.query, top_k=payload.top_k)

    laptop_ids = [lid for lid, _ in raw_results]
    laptops = {lp.id: lp for lp in db.query(Laptop).filter(Laptop.id.in_(laptop_ids)).all()}

    results = []
    for laptop_id, score in raw_results:
        lp = laptops.get(laptop_id)
        if lp is None:
            continue
        results.append(SearchResultItem(laptop=laptop_to_out(lp), similarity_score=round(score, 4)))

    user_engine.log_event(db, current_user.id, "search", {"query": payload.query})

    return SearchResponse(query=payload.query, results=results)
