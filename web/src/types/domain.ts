export interface Laptop {
  id: number;
  model_name: string;
  brand: string;
  cpu_name: string | null;
  gpu_name: string | null;
  ram_gb: number;
  storage_gb: number;
  storage_type: string;
  display_size_inch: number | null;
  display_resolution: string | null;
  refresh_rate_hz: number | null;
  battery_life_hours: number | null;
  weight_kg: number | null;
  price_inr: number;
  release_year: number | null;
  scores: Record<string, number>;
}

export interface SearchResultItem {
  laptop: Laptop;
  similarity_score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

export interface Explanation {
  reasons: string[];
  pros: string[];
  cons: string[];
  confidence_score: number;
  better_alternatives: number[];
  budget_tradeoffs: string[];
}

export interface RetailerLink {
  retailer: string; // "amazon" | "flipkart" | "official_store" | ...
  label: string;    // e.g. "Buy on Amazon"
  url: string;
}

export interface RecommendationItem {
  laptop: Laptop;
  hybrid_score: number;
  score_breakdown: Record<string, number>;
  explanation: Explanation;
  retailer_links: RetailerLink[];
}

export interface RecommendationResponse {
  request_summary: Record<string, unknown>;
  recommendations: RecommendationItem[];
}

export interface CompareResponse {
  laptops: Laptop[];
  winner_by_category: Record<string, string>;
  overall_recommendation: string;
}

export interface BudgetSuggestion {
  laptop: Laptop;
  price_delta_inr: number;
  tradeoff_summary: string;
}

export interface BudgetOptimizeResponse {
  base_laptop: Laptop;
  upgrades: BudgetSuggestion[];
  downgrades: BudgetSuggestion[];
}

export interface AnalyticsResponse {
  total_laptops: number;
  brand_distribution: Record<string, number>;
  cpu_distribution: Record<string, number>;
  gpu_distribution: Record<string, number>;
  price_distribution: Record<string, number>;
  avg_price: number;
  kb_version: string | null;
}

export interface UserPreferences {
  user_id: number;
  preferred_brands: string[];
  budget_min: number;
  budget_max: number;
  primary_use_case: string | null;
  saved_laptop_ids: number[];
}
