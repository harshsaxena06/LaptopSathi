import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ExactLandingPage } from '@/components/landing/ExactLandingPage';
import { AuthModal } from '@/components/landing/AuthModal';

type Mode = 'user' | 'admin';

export function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>('user');
  const [authOpen, setAuthOpen] = useState(false);

  function openAuth() {
    setMode('user');
    setAuthOpen(true);
  }

  // Visiting /admin-login directly is an intentional destination — open the
  // admin sign-in dialog immediately instead of requiring an extra click.
  useEffect(() => {
    if (location.pathname === '/admin-login') {
      setMode('admin');
      setAuthOpen(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Support deep links like /login#laptops (e.g. the About page's CTA) —
  // client-side routing doesn't auto-scroll to a hash target.
  useEffect(() => {
    if (!location.hash) return;
    const id = location.hash.slice(1);
    const el = document.getElementById(id);
    if (el) {
      requestAnimationFrame(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.hash]);

  return (
    <>
      <ExactLandingPage onSignIn={openAuth} onCreateAccount={() => navigate('/register')} />

      <AuthModal
        open={authOpen}
        mode={mode}
        onClose={() => setAuthOpen(false)}
        onSwitchMode={setMode}
      />
    </>
  );
}
