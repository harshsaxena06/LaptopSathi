from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import RecommendationRequest, RecommendationResponse, RecommendationItem
from app.recommendation import engine
from app.utils.serializers import laptop_to_out
from app.personalization import user_engine
from app.auth.dependencies import get_current_user
from app.models.db_models import User
from app.retailer_links.links import build_retailer_links

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferred_brands = payload.preferred_brands
    if not preferred_brands:
        # enrich with learned brand affinity if the user didn't explicitly specify
        inferred = user_engine.infer_brand_affinity(db, current_user.id)
        preferred_brands = inferred or None

    results = engine.recommend(
        db=db,
        query=payload.query,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        use_case=payload.use_case,
        preferred_brands=preferred_brands,
        top_k=payload.top_k,
    )

    items = []
    for r in results:
        laptop_out = laptop_to_out(r["laptop"])
        items.append(
            RecommendationItem(
                laptop=laptop_out,
                hybrid_score=r["hybrid_score"],
                score_breakdown=r["score_breakdown"],
                explanation=r["explanation"],
                # Generated on the fly from brand + model_name — never read
                # from (or written to) the Knowledge Base CSV/DB.
                retailer_links=build_retailer_links(laptop_out.brand, laptop_out.model_name),
            )
        )

    user_engine.log_event(db, current_user.id, "recommend", {
        "query": payload.query, "use_case": payload.use_case,
    })

    return RecommendationResponse(
        request_summary=payload.model_dump(),
        recommendations=items,
    )
