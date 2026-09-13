/**
 * Token storage strategy:
 *  - Access token: kept ONLY in memory (a module-level variable). It never
 *    touches localStorage/sessionStorage, so it can't be read by a
 *    persistence-based XSS payload after the fact — worst case exposure is
 *    the current tab's JS heap for up to ACCESS_TOKEN_EXPIRE_MINUTES.
 *  - Refresh token: persisted so a page reload doesn't force a re-login.
 *    "Remember me" checked -> localStorage (survives browser restarts).
 *    "Remember me" unchecked -> sessionStorage (cleared when the tab closes).
 *
 * This is a pragmatic tradeoff for a client-side SPA talking to a JSON API.
 * The strictly more secure pattern is an httpOnly, Secure, SameSite cookie
 * for the refresh token issued directly by the server — worth migrating to
 * if/when the frontend and API share a parent domain in production.
 */

const REFRESH_TOKEN_KEY = 'laptopsathi_refresh_token';
const REMEMBER_ME_KEY = 'laptopsathi_remember_me';

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function persistRefreshToken(token: string, rememberMe: boolean): void {
  clearRefreshToken();
  const storage = rememberMe ? localStorage : sessionStorage;
  storage.setItem(REFRESH_TOKEN_KEY, token);
  localStorage.setItem(REMEMBER_ME_KEY, rememberMe ? '1' : '0');
}

export function getPersistedRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY) ?? sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearRefreshToken(): void {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(REMEMBER_ME_KEY);
}

export function clearAllTokens(): void {
  accessToken = null;
  clearRefreshToken();
}
