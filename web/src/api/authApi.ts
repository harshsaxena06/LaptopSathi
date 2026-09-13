import { api } from './client';
import { TokenResponse, RegisterStartResult, MessageResponse, User } from '@/types/auth';

export const authApi = {
  /** Step 1 of registration: creates an unverified account and emails a
   * 6-digit code. Does NOT log the user in — see verifyRegistrationOtp. */
  register: (email: string, password: string, fullName?: string) =>
    api.post<RegisterStartResult>('/api/auth/register', { email, password, full_name: fullName || null }, { skipAuth: true }),

  /** Step 2 of registration: confirms the emailed code. On success the
   * account becomes usable and the user is logged in (real tokens). */
  verifyRegistrationOtp: (email: string, otp: string) =>
    api.post<TokenResponse>('/api/auth/register/verify-otp', { email, otp }, { skipAuth: true }),

  resendRegistrationOtp: (email: string) =>
    api.post<MessageResponse>('/api/auth/register/resend-otp', { email }, { skipAuth: true }),

  login: (email: string, password: string, rememberMe: boolean) =>
    api.post<TokenResponse>('/api/auth/login', { email, password, remember_me: rememberMe }, { skipAuth: true }),

  adminLogin: (email: string, password: string) =>
    api.post<TokenResponse>('/api/auth/admin-login', { email, password }, { skipAuth: true }),

  refresh: (refreshToken: string) =>
    api.post<TokenResponse>('/api/auth/refresh', { refresh_token: refreshToken }, { skipAuth: true }),

  logout: (refreshToken: string) =>
    api.post<MessageResponse>('/api/auth/logout', { refresh_token: refreshToken }),

  forgotPassword: (email: string) =>
    api.post<MessageResponse>('/api/auth/forgot-password', { email }, { skipAuth: true }),

  resetPassword: (token: string, newPassword: string) =>
    api.post<MessageResponse>('/api/auth/reset-password', { token, new_password: newPassword }, { skipAuth: true }),

  me: () => api.get<User>('/api/auth/me'),
};
