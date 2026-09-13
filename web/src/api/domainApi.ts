import { api } from './client';
import {
  Laptop, SearchResponse, RecommendationResponse, CompareResponse,
  BudgetOptimizeResponse, AnalyticsResponse, UserPreferences,
} from '@/types/domain';

export interface RecommendRequest {
  query?: string | null;
  budget_min: number;
  budget_max: number;
  use_case?: string | null;
  preferred_brands?: string[] | null;
  top_k: number;
}

export const domainApi = {
  getLaptop: (id: number) => api.get<Laptop>(`/api/laptops/${id}`),

  search: (query: string, topK = 10) =>
    api.post<SearchResponse>('/api/search', { query, top_k: topK }),

  recommend: (payload: RecommendRequest) =>
    api.post<RecommendationResponse>('/api/recommend', payload),

  compare: (laptopIds: number[]) =>
    api.post<CompareResponse>('/api/compare', { laptop_ids: laptopIds }),

  budgetOptimize: (laptopId: number, flexibilityInr: number) =>
    api.post<BudgetOptimizeResponse>('/api/budget-optimizer', {
      laptop_id: laptopId, flexibility_inr: flexibilityInr,
    }),

  getPreferences: () => api.get<UserPreferences>('/api/users/me/preferences'),

  saveLaptop: (laptopId: number) =>
    api.post<UserPreferences>('/api/users/me/save-laptop', { laptop_id: laptopId }),

  unsaveLaptop: (laptopId: number) =>
    api.post<UserPreferences>('/api/users/me/unsave-laptop', { laptop_id: laptopId }),

  getAnalytics: () => api.get<AnalyticsResponse>('/api/analytics'),
};
