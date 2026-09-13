import React, { useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '@/context/ThemeContext';

/**
 * Shared header + footer for lightweight standalone pages (About, Terms,
 * Privacy) that should feel like part of the same site as the landing page
 * without duplicating its full markup.
 */
export function SimplePageChrome({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const rootRef = useRef<HTMLDivElement>(null);
  const isAbout = location.pathname === '/about';

  useEffect(() => {
    const els = rootRef.current?.querySelectorAll('.reveal');
    if (!els || els.length === 0) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.1 },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <div className="exact-landing" ref={rootRef}>
      <header>
        <div className="header-left">
          <Link to="/login" className="logo">
            <span className="logo-mark"><img src="/logo-mark.png" alt="LaptopSathi AI" /></span>
            <span className="logo-word">LaptopSathi <span className="ai-chip">AI</span></span>
          </Link>
        </div>
        <div className="header-actions">
          <Link
            to="/about"
            className={isAbout ? 'about-link active' : 'about-link'}
            aria-current={isAbout ? 'page' : undefined}
          >
            About
          </Link>
          <button
            type="button"
            className="btn btn-primary"
            style={{ padding: '9px 18px', fontSize: 13 }}
            onClick={() => navigate('/login')}
          >
            Sign In
          </button>
          <button type="button" className="theme-btn" aria-label="Toggle theme" onClick={toggleTheme}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
              {theme === 'dark' ? (
                <>
                  <path d="M12 4V2M12 22v-2M4.9 4.9 3.5 3.5M20.5 20.5l-1.4-1.4M4 12H2m20 0h-2M4.9 19.1l-1.4 1.4M20.5 3.5l-1.4 1.4" />
                  <circle cx="12" cy="12" r="5" />
                </>
              ) : (
                <path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z" />
              )}
            </svg>
          </button>
        </div>
      </header>

      <main>{children}</main>

      <footer>
        <div className="footer-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span className="logo-mark"><img src="/logo-mark.png" alt="LaptopSathi AI" /></span>
            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14.5 }}>LaptopSathi AI</div>
              <div className="footer-tagline">Your Intelligent Laptop Decision Platform</div>
            </div>
          </div>
          <div className="footer-meta">
            <div className="footer-links">
              <Link to="/about">About</Link>
              <Link to="/terms">Terms</Link>
              <Link to="/privacy">Privacy</Link>
            </div>
          </div>
        </div>
        <div className="footer-bottom">© {new Date().getFullYear()} LaptopSathi AI</div>
      </footer>
    </div>
  );
}
