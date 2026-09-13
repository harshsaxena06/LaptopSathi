import { ApiError, ApiErrorBody, TokenResponse } from '@/types/auth';
import {
  getAccessToken, setAccessToken, getPersistedRefreshToken,
  persistRefreshToken, clearAllTokens,
} from './tokenStore';

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

/** Paths that must never trigger the refresh-and-retry flow (avoids loops). */
const NO_REFRESH_PATHS = ['/api/auth/login', '/api/auth/admin-login', '/api/auth/register', '/api/auth/refresh'];

let refreshInFlight: Promise<boolean> | null = null;

/** Called by AuthContext once at boot, and again after login/refresh, so the
 * client knows how to persist the next rotated refresh token. */
let rememberMeFlag = false;
export function setRememberMe(value: boolean) {
  rememberMeFlag = value;
}

async function doRefresh(): Promise<boolean> {
  const raw = getPersistedRefreshToken();
  if (!raw) return false;

  try {
    const res = await fetch(`${BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: raw }),
    });
    if (!res.ok) {
      clearAllTokens();
      return false;
    }
    const data: TokenResponse = await res.json();
    setAccessToken(data.access_token);
    persistRefreshToken(data.refresh_token, rememberMeFlag);
    return true;
  } catch {
    return false;
  }
}

/** Ensures only one refresh request is in flight even if several API calls
 * 401 at the same time (e.g. a burst of parallel requests on page load). */
function refreshOnce(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = doRefresh().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { skipAuth, headers, ...rest } = options;

  const doFetch = async (): Promise<Response> => {
    const isFormData = typeof FormData !== 'undefined' && rest.body instanceof FormData;
    const finalHeaders: Record<string, string> = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(headers as Record<string, string> | undefined),
    };
    const token = getAccessToken();
    if (token && !skipAuth) {
      finalHeaders['Authorization'] = `Bearer ${token}`;
    }
    let response: Response;
    try {
      response = await fetch(`${BASE_URL}${path}`, { ...rest, headers: finalHeaders });
    } catch {
      throw new ApiError('Could not reach the server. Check your connection and try again.', 'NETWORK_ERROR', 0);
    }
    return response;
  };

  let res = await doFetch();

  const canRetryWithRefresh = res.status === 401 && !skipAuth && !NO_REFRESH_PATHS.includes(path);
  if (canRetryWithRefresh) {
    const refreshed = await refreshOnce();
    if (refreshed) {
      res = await doFetch();
    }
  }

  if (!res.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await res.json();
    } catch {
      /* non-JSON error body */
    }
    const message = body?.error?.message || `Request failed (${res.status})`;
    const code = body?.error?.code || 'UNKNOWN_ERROR';
    throw new ApiError(message, code, res.status, body?.error?.details);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) => apiRequest<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiRequest<T>(path, { ...options, method: 'POST', body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiRequest<T>(path, { ...options, method: 'PUT', body: body !== undefined ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiRequest<T>(path, { ...options, method: 'PATCH', body: body !== undefined ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string, options?: RequestOptions) => apiRequest<T>(path, { ...options, method: 'DELETE' }),
  /** For multipart/form-data uploads (e.g. the admin KB file upload) — do
   * not JSON.stringify a FormData body, and let the browser set the
   * multipart boundary itself. */
  upload: <T>(path: string, formData: FormData, options?: RequestOptions) =>
    apiRequest<T>(path, { ...options, method: 'POST', body: formData }),
};
