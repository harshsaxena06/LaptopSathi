import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '@/context/ThemeContext';
import { LandingIcon, LandingStarIcon } from '@/data/landingIcons';
import { LAPTOPS, FEATURES, STEPS, VALUES } from '@/data/landingContent';

/**
 * Pixel-exact port of landing-preview.html — same markup, same CSS
 * (scoped under .exact-landing in styles/landing.css), same data,
 * same real product photography. Only the fake "visual mock" sign-in
 * modal from the original file was swapped for the app's real AuthModal
 * (wired in via onSignIn), since that modal was explicitly not
 * connected to real auth in the source file.
 */

interface Props {
  onSignIn: () => void;
  onCreateAccount: () => void;
}

export function ExactLandingPage({ onSignIn, onCreateAccount }: Props) {
  const { theme, toggleTheme } = useTheme();
  const [activeId, setActiveId] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const sliderRef = useRef<HTMLDivElement>(null);

  const active = LAPTOPS.find((l) => l.id === activeId) ?? null;

  // ---- Scroll reveal (same threshold/behavior as the source script) ----
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
      { threshold: 0.15 },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  function scrollSlider(dir: number) {
    const track = sliderRef.current;
    if (!track) return;
    const card = track.querySelector('.laptop-card') as HTMLElement | null;
    const step = card ? card.getBoundingClientRect().width + 22 : 278;
    track.scrollBy({ left: dir * step * 2, behavior: 'smooth' });
  }

  function selectLaptop(id: string) {
    setActiveId((cur) => (cur === id ? null : id));
  }

  return (
    <div className="exact-landing" ref={rootRef}>
      <header>
        <div className="header-left">
          <a href="#" className="logo">
            <span className="logo-mark"><img src="/logo-mark.png" alt="LaptopSathi AI" /></span>
            <span className="logo-word">LaptopSathi <span className="ai-chip">AI</span></span>
          </a>
        </div>
        <div className="header-actions">
          <Link to="/about" className="about-link">About</Link>
          <button
            type="button"
            className="btn btn-primary"
            style={{ padding: '9px 18px', fontSize: 13 }}
            onClick={onSignIn}
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

      <main>
        <section className="hero">
          <div className="hero-field" aria-hidden="true">
            <div className="hero-orb hero-orb-a" />
            <div className="hero-orb hero-orb-b" />
            <div className="hero-grid" />
            <span className="hero-dot" style={{ top: '14%', left: '9%', animationDelay: '0s' }} />
            <span className="hero-dot" style={{ top: '24%', left: '88%', animationDelay: '1.4s' }} />
            <span className="hero-dot" style={{ top: '70%', left: '6%', animationDelay: '2.6s' }} />
            <span className="hero-dot" style={{ top: '76%', left: '91%', animationDelay: '.7s' }} />
            <span className="hero-dot" style={{ top: '8%', left: '50%', animationDelay: '3.2s' }} />
            <span className="hero-dot" style={{ top: '56%', left: '95%', animationDelay: '1.9s' }} />
          </div>
          <div className="hero-inner">
            <div className="hero-illustration" aria-hidden="true">
              <svg viewBox="0 0 306 216">
                <defs>
                  <linearGradient id="screenGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stopColor="var(--accent-soft)" />
                    <stop offset="1" stopColor="var(--surface-2)" />
                  </linearGradient>
                  <linearGradient id="baseGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor="var(--border-strong)" stopOpacity=".5" />
                    <stop offset="1" stopColor="var(--border-strong)" stopOpacity=".15" />
                  </linearGradient>
                  <radialGradient id="shadowGrad" cx="50%" cy="50%" r="50%">
                    <stop offset="0" stopColor="var(--text-3)" stopOpacity=".28" />
                    <stop offset="1" stopColor="var(--text-3)" stopOpacity="0" />
                  </radialGradient>
                  <radialGradient id="cardGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0" stopColor="var(--accent)" stopOpacity=".35" />
                    <stop offset="1" stopColor="var(--accent)" stopOpacity="0" />
                  </radialGradient>
                  <linearGradient id="sheenGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor="#ffffff" stopOpacity=".55" />
                    <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
                  </linearGradient>
                  <filter id="softBlur" x="-60%" y="-60%" width="220%" height="220%">
                    <feGaussianBlur stdDeviation="10" />
                  </filter>
                </defs>

                <ellipse cx="153" cy="193" rx="86" ry="12" fill="url(#shadowGrad)" />
                <path d="M90 150 L216 150 L240 171 L66 171 Z" fill="url(#baseGrad)" stroke="var(--border-strong)" strokeWidth={1} />

                <g className="card-group">
                  <circle cx="153" cy="97" r="72" fill="url(#cardGlow)" filter="url(#softBlur)" />

                  <line x1="52" y1="84" x2="98" y2="99" stroke="var(--border-strong)" strokeWidth={1} strokeDasharray="3 3" />
                  <line x1="52" y1="149" x2="98" y2="125" stroke="var(--border-strong)" strokeWidth={1} strokeDasharray="3 3" />
                  <line x1="254" y1="73" x2="208" y2="94" stroke="var(--border-strong)" strokeWidth={1} strokeDasharray="3 3" />
                  <line x1="254" y1="147" x2="208" y2="123" stroke="var(--border-strong)" strokeWidth={1} strokeDasharray="3 3" />

                  <circle className="dot d1" cx="52" cy="84" r="6.5" fill="var(--accent-soft)" />
                  <circle className="dot d1" cx="52" cy="84" r="3.5" fill="var(--accent)" />
                  <circle className="dot d2" cx="52" cy="149" r="6.5" fill="var(--accent-soft)" />
                  <circle className="dot d2" cx="52" cy="149" r="3.5" fill="var(--accent)" />
                  <circle className="dot d3" cx="254" cy="73" r="6.5" fill="var(--accent-soft)" />
                  <circle className="dot d3" cx="254" cy="73" r="3.5" fill="var(--accent)" />
                  <circle className="dot d4" cx="254" cy="147" r="6.5" fill="var(--accent-soft)" />
                  <circle className="dot d4" cx="254" cy="147" r="3.5" fill="var(--accent)" />

                  <rect x="95" y="52" width="116" height="90" rx="15" fill="var(--surface)" stroke="var(--border-strong)" strokeWidth={1.5} />
                  <rect x="95" y="52" width="116" height="90" rx="15" fill="url(#sheenGrad)" opacity=".5" />
                  <rect x="109" y="73" width="88" height="51" rx="9" fill="url(#screenGrad)" />
                  <rect x="118" y="83" width="60" height="7.5" rx="3.75" fill="var(--accent)" />
                  <rect x="118" y="98" width="70" height="7.5" rx="3.75" fill="var(--accent)" opacity=".8" />
                  <rect x="118" y="113" width="46" height="7.5" rx="3.75" fill="var(--accent)" opacity=".6" />
                </g>
              </svg>
            </div>
            <h1>
              Your
              {' '}
              <span className="hero-emphasis">
                Intelligent Laptop
                <svg viewBox="0 0 320 14" preserveAspectRatio="none"><path d="M4 9C60 2 260 2 316 9" /></svg>
              </span>
              {' '}
              Decision Platform
            </h1>
            <p className="lede">Find the right laptop with AI-powered recommendations, intelligent search, hardware comparisons, and personalized insights — all built on a real laptop knowledge base.</p>
            <div className="hero-cta-row">
              <a href="#laptops" className="btn btn-primary btn-lg">Explore Laptops</a>
            </div>
            <p className="hero-below">Already have an account? <button type="button" onClick={onSignIn}>Sign in</button></p>
          </div>
        </section>

        <section id="laptops" className="band laptop-section">
          <div className="section-head reveal">
            <span className="section-eyebrow">Explore Laptops</span>
            <h2>Slide through picks, tap one to dig in</h2>
            <p>A quick browse of real configurations across budgets and use cases — tap any card to see the full breakdown.</p>
          </div>
          <div className="laptop-stage reveal">
            <button type="button" className="slider-arrow arrow-prev" aria-label="Scroll left" onClick={() => scrollSlider(-1)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
            </button>
            <div className="laptop-slider" ref={sliderRef}>
              {LAPTOPS.map((l) => {
                const isActive = l.id === activeId;
                return (
                  <button
                    key={l.id}
                    type="button"
                    className={`laptop-card${isActive ? ' active' : ''}`}
                    aria-expanded={isActive}
                    onClick={() => selectLaptop(l.id)}
                  >
                    {l.badge && <span className="laptop-badge">{l.badge}</span>}
                    <div className="laptop-visual"><img src={l.img} alt={l.name} loading="lazy" /></div>
                    <div className="laptop-card-body">
                      <span className="laptop-tag" style={{ color: `var(--${l.hue})` }}>{l.tag}</span>
                      <h3>{l.name}</h3>
                      <div className="laptop-rating"><LandingStarIcon fill="var(--amber)" stroke="none" /><span>{l.rating} ({l.reviews})</span></div>
                      <div className="laptop-price-row">
                        <span className="laptop-price">{l.price}</span>
                        {l.mrp && (
                          <>
                            <span className="laptop-price-strike">{l.mrp}</span>
                            <span className="laptop-discount">{l.discount}</span>
                          </>
                        )}
                      </div>
                      <div className="laptop-chip-row">
                        {l.chips.map((c) => <span className="laptop-chip" key={c}>{c}</span>)}
                      </div>
                      <div className="laptop-expand-row"><span>Full specs</span><LandingIcon name="chevrondown" /></div>
                    </div>
                  </button>
                );
              })}
            </div>
            <button type="button" className="slider-arrow arrow-next" aria-label="Scroll right" onClick={() => scrollSlider(1)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6" /></svg>
            </button>
          </div>
          <div className="laptop-detail">
            {active && (
              <div className="laptop-detail-panel open">
                <div className="laptop-detail-inner">
                  <div className="laptop-detail-gallery">
                    <div className="laptop-detail-visual"><img src={active.img} alt={active.name} /></div>
                    {active.altImg && (
                      <div className="laptop-detail-visual-alt"><img src={active.altImg} alt={`${active.name} alternate view`} /></div>
                    )}
                  </div>
                  <div className="laptop-detail-body">
                    <span className="laptop-tag" style={{ color: `var(--${active.hue})` }}>{active.tag}</span>
                    <h3>{active.name}</h3>
                    <div className="laptop-rating"><LandingStarIcon fill="var(--amber)" stroke="none" /><span>{active.rating} ({active.reviews} ratings)</span></div>
                    <p className="laptop-detail-tagline">{active.tagline}</p>
                    <dl className="laptop-spec-grid">
                      {Object.entries(active.specs).map(([k, v]) => (
                        <div className="laptop-spec" key={k}><dt>{k}</dt><dd>{v}</dd></div>
                      ))}
                    </dl>
                    <div className="laptop-detail-footer">
                      <div className="laptop-detail-price-row">
                        <span className="laptop-detail-price">{active.price}</span>
                        {active.mrp && (
                          <>
                            <span className="laptop-price-strike">{active.mrp}</span>
                            <span className="laptop-discount">{active.discount}</span>
                          </>
                        )}
                      </div>
                      <button type="button" className="btn btn-primary" onClick={onSignIn}>Get this recommendation</button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        <section id="features" className="band">
          <div className="section-head reveal">
            <span className="section-eyebrow">Why LaptopSathi</span>
            <h2>Everything you need to make a smarter laptop decision</h2>
            <p>LaptopSathi combines AI, hardware knowledge, and personalized recommendations to help you choose with confidence.</p>
          </div>
          <div className="feature-grid">
            {FEATURES.map((f) => (
              <div className="f-card reveal" key={f.title}>
                <div className="f-icon" style={{ background: `var(--${f.hue}-soft)`, color: `var(--${f.hue})` }}>
                  <LandingIcon name={f.icon} />
                </div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="band band-alt">
          <div className="section-head reveal">
            <span className="section-eyebrow">The process</span>
            <h2>From confusion to confidence</h2>
          </div>
          <div className="steps">
            {STEPS.map((s, i) => (
              <div className="step reveal" key={s.n}>
                <div className="step-top">
                  <span className="step-num">{s.n}</span>
                  {i < STEPS.length - 1 && <span className="step-connector" />}
                </div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="about" className="band">
          <div className="trust-panel reveal">
            <div className="section-head" style={{ marginBottom: 0 }}>
              <h2>Not just another laptop comparison site</h2>
              <p>Most laptop websites give you hundreds of specifications and affiliate links. LaptopSathi is designed to help you actually make a decision.</p>
            </div>
            <div className="value-row">
              {VALUES.map((v) => (
                <div className="value-item reveal" key={v.title}>
                  <div className="f-icon" style={{ background: `var(--${v.hue}-soft)`, color: `var(--${v.hue})` }}>
                    <LandingIcon name={v.icon} />
                  </div>
                  <h3>{v.title}</h3>
                  <p>{v.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

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
              <button type="button" onClick={onSignIn}>Sign in</button>
              <button type="button" onClick={onCreateAccount}>Create account</button>
            </div>
          </div>
        </div>
        <div className="footer-bottom">© {new Date().getFullYear()} LaptopSathi AI</div>
      </footer>
    </div>
  );
}
