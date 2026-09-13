import { api } from './client';

export interface KBUploadResult {
  version_tag: string;
  record_count: number;
  invalid_rows: number;
  duplicate_rows: number;
  index_rebuilt: boolean;
  index_error: string | null;
}

export interface KBVersion {
  version_tag: string;
  source_file: string | null;
  record_count: number;
  notes: string | null;
  created_at: string;
}

export interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface SystemSettings {
  app_name: string;
  env: string;
  embedding_model: string;
  access_token_expire_minutes: number;
  refresh_token_expire_days: number;
  max_failed_login_attempts: number;
  account_lock_minutes: number;
  recommendation_weights: Record<string, number>;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
}

/**
 * Everything an admin needs to manage the running app from the UI — no
 * backend/CLI access required: upload a fresh dataset, force a search-index
 * rebuild, browse dataset version history, promote/deactivate users, read
 * the live config, and tail recent server logs.
 */
export const adminApi = {
  uploadKnowledgeBase: (file: File, notes: string) => {
    const form = new FormData();
    form.append('file', file);
    // The backend takes `notes` as a query parameter on this endpoint
    // (FastAPI treats any plain scalar param alongside a File(...) upload
    // as a query param, not a form field) — so it goes on the URL, not in
    // the FormData body.
    const qs = notes.trim() ? `?notes=${encodeURIComponent(notes.trim())}` : '';
    return api.upload<KBUploadResult>(`/api/admin/knowledge-base/upload${qs}`, form);
  },
  rebuildIndex: () => api.post<{ vectors_indexed: number }>('/api/admin/knowledge-base/rebuild-index'),
  listVersions: () => api.get<KBVersion[]>('/api/admin/knowledge-base/versions'),
  listUsers: () => api.get<AdminUser[]>('/api/admin/users'),
  updateUser: (id: number, payload: { role?: string; is_active?: boolean }) =>
    api.patch<AdminUser>(`/api/admin/users/${id}`, payload),
  getSettings: () => api.get<SystemSettings>('/api/admin/settings'),
  getLogs: (limit = 200) => api.get<LogEntry[]>(`/api/admin/logs?limit=${limit}`),
};
