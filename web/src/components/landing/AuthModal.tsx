import React, { useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthCard } from '@/components/auth/AuthCard';
import { LoginForm } from '@/components/auth/LoginForm';
import { AdminLoginForm } from '@/components/auth/AdminLoginForm';
import { CloseIcon } from '@/components/Icons';

type Mode = 'user' | 'admin';

interface Props {
  open: boolean;
  mode: Mode;
  onClose: () => void;
  onSwitchMode: (mode: Mode) => void;
}

/**
 * The exact same LoginForm/AdminLoginForm/AuthCard the app has always used —
 * just presented as an on-demand dialog instead of a section permanently
 * embedded in the landing page. No auth logic lives here; this is purely a
 * presentation wrapper.
 */
export function AuthModal({ open, mode, onClose, onSwitchMode }: Props) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialogRef.current?.focus();

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="auth-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.18 }}
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) onClose();
          }}
        >
          <motion.div
            className="auth-modal-dialog"
            role="dialog"
            aria-modal="true"
            aria-label={mode === 'admin' ? 'Admin sign in' : 'Sign in'}
            tabIndex={-1}
            ref={dialogRef}
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.98 }}
            transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
          >
            <button
              type="button"
              className="auth-modal-close"
              onClick={onClose}
              aria-label="Close sign in dialog"
            >
              <CloseIcon width={16} height={16} />
            </button>
            <AuthCard>
              <AnimatePresence mode="wait" initial={false}>
                <motion.div
                  key={mode}
                  initial={{ opacity: 0, x: mode === 'admin' ? 24 : -24 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: mode === 'admin' ? -24 : 24 }}
                  transition={{ duration: 0.24, ease: [0.4, 0, 0.2, 1] }}
                >
                  {mode === 'user' ? (
                    <LoginForm onSwitchToAdmin={() => onSwitchMode('admin')} />
                  ) : (
                    <AdminLoginForm onSwitchToUser={() => onSwitchMode('user')} />
                  )}
                </motion.div>
              </AnimatePresence>
            </AuthCard>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
