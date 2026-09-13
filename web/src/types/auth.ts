export type Role = 'user' | 'admin';

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: Role;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

/** Result of POST /api/auth/register — starts registration, sends an email
 * OTP, and does NOT log the user in yet (see RegisterVerifyOtpResult). */
export interface RegisterStartResult {
  message: string;
  email: string;
}

export interface MessageResponse {
  message: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
  }
}
