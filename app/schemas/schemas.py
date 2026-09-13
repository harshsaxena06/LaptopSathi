"""Pydantic schemas — the API contract. Frontend depends only on these shapes."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ---------- Laptop ----------

class LaptopOut(BaseModel):
    id: int
    model_name: str
    brand: str
    cpu_name: Optional[str] = None
    gpu_name: Optional[str] = None
    ram_gb: int
    storage_gb: int
    storage_type: str
    display_size_inch: Optional[float] = None
    display_resolution: Optional[str] = None
    refresh_rate_hz: Optional[int] = None
    battery_life_hours: Optional[float] = None
    weight_kg: Optional[float] = None
    price_inr: float
    release_year: Optional[int] = None
    scores: Dict[str, float] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ---------- Semantic Search ----------

class SearchQuery(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)


class SearchResultItem(BaseModel):
    laptop: LaptopOut
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]


# ---------- Recommendation ----------

class RecommendationRequest(BaseModel):
    query: Optional[str] = Field(default=None, max_length=500)
    budget_min: float = Field(default=0, ge=0)
    budget_max: float = Field(default=300000, gt=0)
    use_case: Optional[str] = None  # programming / gaming / ai_ml / video_editing / business / student
    preferred_brands: Optional[List[str]] = None
    top_k: int = Field(default=5, ge=1, le=25)


class Explanation(BaseModel):
    reasons: List[str]
    pros: List[str]
    cons: List[str]
    confidence_score: float
    better_alternatives: List[int] = Field(default_factory=list)  # laptop ids
    budget_tradeoffs: List[str] = Field(default_factory=list)


class RetailerLink(BaseModel):
    retailer: str  # e.g. "amazon" / "flipkart" / "official_store"
    label: str     # e.g. "Buy on Amazon"
    url: str


class RecommendationItem(BaseModel):
    laptop: LaptopOut
    hybrid_score: float
    score_breakdown: Dict[str, float]
    explanation: Explanation
    retailer_links: List[RetailerLink] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    request_summary: Dict[str, Any]
    recommendations: List[RecommendationItem]


# ---------- Comparison ----------

class CompareRequest(BaseModel):
    laptop_ids: List[int] = Field(min_length=2, max_length=6)


class CompareResponse(BaseModel):
    laptops: List[LaptopOut]
    winner_by_category: Dict[str, str]  # category -> model_name
    overall_recommendation: str


# ---------- Budget Optimizer ----------

class BudgetOptimizeRequest(BaseModel):
    laptop_id: int
    flexibility_inr: float = Field(default=10000, ge=0, le=500000)


class BudgetSuggestion(BaseModel):
    laptop: LaptopOut
    price_delta_inr: float
    tradeoff_summary: str


class BudgetOptimizeResponse(BaseModel):
    base_laptop: LaptopOut
    upgrades: List[BudgetSuggestion]
    downgrades: List[BudgetSuggestion]


# ---------- Price Intelligence ----------

class PricePoint(BaseModel):
    price_inr: float
    recorded_at: str
    source: str


class PriceIntelligenceResponse(BaseModel):
    laptop_id: int
    current_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    trend: str  # "rising" / "falling" / "stable"
    history: List[PricePoint]


# ---------- User Preferences / Personalization ----------

class UserPreferenceUpdate(BaseModel):
    """No user_id here — the authenticated caller's identity comes from the
    JWT (see app.auth.dependencies.get_current_user), never from the body."""
    preferred_brands: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    primary_use_case: Optional[str] = None


class UserPreferenceOut(BaseModel):
    user_id: int
    preferred_brands: List[str]
    budget_min: float
    budget_max: float
    primary_use_case: Optional[str]
    saved_laptop_ids: List[int]

    class Config:
        from_attributes = True


class SaveLaptopRequest(BaseModel):
    laptop_id: int


# ---------- Similar Laptop Finder ----------

class SimilarLaptopResponse(BaseModel):
    reference_laptop_id: int
    similar: List[SearchResultItem]


# ---------- Analytics ----------

class AnalyticsResponse(BaseModel):
    total_laptops: int
    brand_distribution: Dict[str, int]
    cpu_distribution: Dict[str, int]
    gpu_distribution: Dict[str, int]
    price_distribution: Dict[str, int]  # bucketed
    avg_price: float
    kb_version: Optional[str] = None
