import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, TokenResponse, ApiError } from '@/types/auth';
import { authApi } from '@/api/authApi';
import {
  setAccessToken, persistRefreshToken, getPersistedRefreshToken, clearAllTokens,
} from '@/api/tokenStore';
import { setRememberMe as setClientRememberMe } from '@/api/client';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;
  adminLogin: (email: string, password: string) => Promise<void>;
  /** Step 1 of registration — sends an email OTP, does not log in. Returns
   * the email so the caller can show it back on the OTP-entry screen. */
  registerStart: (email: string, password: string, fullName?: string) => Promise<{ email: string; message: string }>;
  /** Step 2 of registration — confirms the OTP and logs the user in. */
  verifyRegistrationOtp: (email: string, otp: string) => Promise<void>;
  resendRegistrationOtp: (email: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function applySession(data: TokenResponse, rememberMe: boolean) {
  setClientRememberMe(rememberMe);
  setAccessToken(data.access_token);
  persistRefreshToken(data.refresh_token, rememberMe);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On boot: if a refresh token was persisted from a previous visit, silently
  // exchange it for a fresh access token and hydrate the user — this is what
  // makes "Remember me" actually keep you logged in across reloads.
  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      const raw = getPersistedRefreshToken();
      if (!raw) {
        setIsLoading(false);
        return;
      }
      try {
        const data = await authApi.refresh(raw);
        if (cancelled) return;
        applySession(data, true);
        setUser(data.user);
      } catch {
        clearAllTokens();
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    bootstrap();
    return () => { cancelled = true; };
  }, []);

  const login = useCallback(async (email: string, password: string, rememberMe: boolean) => {
    const data = await authApi.login(email, password, rememberMe);
    applySession(data, rememberMe);
    setUser(data.user);
  }, []);

  const adminLogin = useCallback(async (email: string, password: string) => {
    const data = await authApi.adminLogin(email, password);
    applySession(data, false);
    setUser(data.user);
  }, []);

  const registerStart = useCallback(async (email: string, password: string, fullName?: string) => {
    const data = await authApi.register(email, password, fullName);
    return { email: data.email, message: data.message };
  }, []);

  const verifyRegistrationOtp = useCallback(async (email: string, otp: string) => {
    const data = await authApi.verifyRegistrationOtp(email, otp);
    applySession(data, false);
    setUser(data.user);
  }, []);

  const resendRegistrationOtp = useCallback(async (email: string) => {
    await authApi.resendRegistrationOtp(email);
  }, []);

  const logout = useCallback(async () => {
    const raw = getPersistedRefreshToken();
    try {
      if (raw) await authApi.logout(raw);
    } catch {
      /* best-effort — clear local state regardless */
    } finally {
      clearAllTokens();
      setUser(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const me = await authApi.me();
      setUser(me);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        clearAllTokens();
        setUser(null);
      }
    }
  }, []);

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    adminLogin,
    registerStart,
    verifyRegistrationOtp,
    resendRegistrationOtp,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
