import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { RegisterForm } from '../RegisterForm';
import { ApiError } from '@/types/auth';

const registerStart = vi.fn();
const verifyRegistrationOtp = vi.fn();
const resendRegistrationOtp = vi.fn();
const showToast = vi.fn();
const navigate = vi.fn();

vi.mock('@/context/AuthContext', () => ({
  useAuth: () => ({ registerStart, verifyRegistrationOtp, resendRegistrationOtp }),
}));
vi.mock('@/context/ToastContext', () => ({
  useToast: () => ({ showToast }),
}));
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigate };
});

function fillStepOne() {
  fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Alice Rivera' } });
  fireEvent.change(screen.getByLabelText(/^email$/i), { target: { value: 'alice@example.com' } });
  fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'StrongPass1' } });
  fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'StrongPass1' } });
  fireEvent.click(screen.getByLabelText(/agree to the/i));
  fireEvent.click(screen.getByRole('button', { name: /create account/i }));
}

describe('RegisterForm — two-step email OTP verification', () => {
  beforeEach(() => {
    registerStart.mockReset();
    verifyRegistrationOtp.mockReset();
    resendRegistrationOtp.mockReset();
    navigate.mockReset();
  });

  it('validates required fields before calling registerStart', () => {
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(registerStart).not.toHaveBeenCalled();
    expect(screen.getByText(/enter your name/i)).toBeInTheDocument();
  });

  it('rejects mismatched passwords', () => {
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Alice' } });
    fireEvent.change(screen.getByLabelText(/^email$/i), { target: { value: 'alice@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'StrongPass1' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'Different1' } });
    fireEvent.click(screen.getByLabelText(/agree to the/i));
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(registerStart).not.toHaveBeenCalled();
    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
  });

  it('moves to the OTP step after a successful registerStart, without navigating yet', async () => {
    registerStart.mockResolvedValueOnce({ email: 'alice@example.com', message: 'sent' });
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);

    fillStepOne();

    expect(await screen.findByText(/verify your email/i)).toBeInTheDocument();
    expect(screen.getByText(/alice@example\.com/i)).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it('verifies the OTP and navigates to the dashboard on success', async () => {
    registerStart.mockResolvedValueOnce({ email: 'alice@example.com', message: 'sent' });
    verifyRegistrationOtp.mockResolvedValueOnce(undefined);
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);

    fillStepOne();
    await screen.findByLabelText(/verification code/i);

    fireEvent.change(screen.getByLabelText(/verification code/i), { target: { value: '482913' } });
    fireEvent.click(screen.getByRole('button', { name: /verify and create account/i }));

    await waitFor(() => expect(verifyRegistrationOtp).toHaveBeenCalledWith('alice@example.com', '482913'));
    await waitFor(() => expect(navigate).toHaveBeenCalledWith('/dashboard'));
  });

  it('shows an error and does not navigate when the OTP is rejected', async () => {
    registerStart.mockResolvedValueOnce({ email: 'alice@example.com', message: 'sent' });
    verifyRegistrationOtp.mockRejectedValueOnce(
      new ApiError('That code is incorrect or has expired.', 'INVALID_REQUEST', 400),
    );
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);

    fillStepOne();
    await screen.findByLabelText(/verification code/i);
    fireEvent.change(screen.getByLabelText(/verification code/i), { target: { value: '000000' } });
    fireEvent.click(screen.getByRole('button', { name: /verify and create account/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/incorrect or has expired/i);
    expect(navigate).not.toHaveBeenCalled();
  });

  it('lets the user resend the code once the cooldown expires', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    registerStart.mockResolvedValueOnce({ email: 'alice@example.com', message: 'sent' });
    resendRegistrationOtp.mockResolvedValueOnce(undefined);
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);

    fillStepOne();
    await screen.findByLabelText(/verification code/i);

    // Freshly shown: resend is disabled during the cooldown.
    expect(screen.getByRole('button', { name: /resend code/i })).toBeDisabled();

    await vi.advanceTimersByTimeAsync(30_000);

    expect(screen.getByRole('button', { name: /^resend code$/i })).not.toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: /^resend code$/i }));
    await waitFor(() => expect(resendRegistrationOtp).toHaveBeenCalledWith('alice@example.com'));
    vi.useRealTimers();
  });

  it('lets the user go back and use a different email', async () => {
    registerStart.mockResolvedValueOnce({ email: 'alice@example.com', message: 'sent' });
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);

    fillStepOne();
    await screen.findByLabelText(/verification code/i);

    fireEvent.click(screen.getByRole('button', { name: /use a different email/i }));
    expect(await screen.findByRole('button', { name: /create account/i })).toBeInTheDocument();
  });
});
