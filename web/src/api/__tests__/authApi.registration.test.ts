import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { authApi } from '../authApi';
import { clearAllTokens } from '../tokenStore';

function mockFetchOnce(body: unknown, status = 200) {
  return vi.fn().mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response);
}

describe('authApi — registration email-OTP endpoints', () => {
  beforeEach(() => {
    clearAllTokens();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('posts to /api/auth/register without an Authorization header', async () => {
    const fetchMock = mockFetchOnce({ message: 'sent', email: 'alice@example.com' }, 201);
    vi.stubGlobal('fetch', fetchMock);

    const res = await authApi.register('alice@example.com', 'StrongPass1', 'Alice');

    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/api/auth/register');
    expect(options.method).toBe('POST');
    expect(JSON.parse(options.body as string)).toEqual({
      email: 'alice@example.com', password: 'StrongPass1', full_name: 'Alice',
    });
    expect(options.headers.Authorization).toBeUndefined();
    expect(res.email).toBe('alice@example.com');
  });

  it('posts email and otp to /api/auth/register/verify-otp', async () => {
    const fetchMock = mockFetchOnce({
      access_token: 'a', refresh_token: 'r', token_type: 'bearer', expires_in: 900,
      user: { id: 1, email: 'alice@example.com', full_name: 'Alice', role: 'user', is_verified: true, created_at: '2024-01-01T00:00:00' },
    });
    vi.stubGlobal('fetch', fetchMock);

    await authApi.verifyRegistrationOtp('alice@example.com', '482913');

    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/api/auth/register/verify-otp');
    expect(JSON.parse(options.body as string)).toEqual({ email: 'alice@example.com', otp: '482913' });
  });

  it('posts to /api/auth/register/resend-otp', async () => {
    const fetchMock = mockFetchOnce({ message: 'If that email has a pending registration, a new code has been sent.' });
    vi.stubGlobal('fetch', fetchMock);

    await authApi.resendRegistrationOtp('alice@example.com');

    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/api/auth/register/resend-otp');
    expect(JSON.parse(options.body as string)).toEqual({ email: 'alice@example.com' });
  });

  it('surfaces a rejected OTP as an ApiError', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: { message: 'That code is incorrect or has expired.', code: 'INVALID_REQUEST' } }),
    } as Response);
    vi.stubGlobal('fetch', fetchMock);

    await expect(authApi.verifyRegistrationOtp('alice@example.com', '000000')).rejects.toMatchObject({
      message: 'That code is incorrect or has expired.',
      code: 'INVALID_REQUEST',
      status: 400,
    });
  });

  it('login still posts email/password/remember_me to /api/auth/login', async () => {
    const fetchMock = mockFetchOnce({
      access_token: 'a', refresh_token: 'r', token_type: 'bearer', expires_in: 900,
      user: { id: 1, email: 'alice@example.com', full_name: 'Alice', role: 'user', is_verified: true, created_at: '2024-01-01T00:00:00' },
    });
    vi.stubGlobal('fetch', fetchMock);

    await authApi.login('alice@example.com', 'StrongPass1', true);

    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/api/auth/login');
    expect(JSON.parse(options.body as string)).toEqual({
      email: 'alice@example.com', password: 'StrongPass1', remember_me: true,
    });
  });
});
