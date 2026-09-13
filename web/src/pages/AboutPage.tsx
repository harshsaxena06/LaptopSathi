import React from 'react';
import { LandingIcon } from '@/data/landingIcons';
import { FEATURES, STEPS } from '@/data/landingContent';
import { GithubIcon, LinkedinIcon } from '@/components/Icons';
import { SimplePageChrome } from '@/components/landing/SimplePageChrome';

const SOCIAL_LINKS = [
  { label: 'LinkedIn', href: 'https://www.linkedin.com/in/harshsaxena06/', Icon: LinkedinIcon },
  { label: 'GitHub', href: 'https://github.com/harshsaxena06', Icon: GithubIcon },
];

const WHAT_IT_IS = [
  { strong: 'AI-powered recommendations', text: 'based on your budget, use case, and priorities.' },
  { strong: 'Semantic search', text: 'describe what you need in plain language, no filters required.' },
  { strong: 'A real laptop knowledge base', text: 'not scraped listings or marketing copy.' },
  { strong: 'Explainable results', text: 'every recommendation comes with the reasoning behind it.' },
  { strong: 'No affiliate bias', text: 'nothing on this site is sponsored or paid placement.' },
];

const PERSONAS = [
  { icon: 'graduationcap', strong: 'Students', text: 'laptops for classes, coding, and projects on a real budget.' },
  { icon: 'code', strong: 'Developers', text: 'processors, RAM, thermals, and portability that hold up to real workloads.' },
  { icon: 'gamepad', strong: 'Gamers', text: 'GPU performance, display quality, and value.' },
  { icon: 'palette', strong: 'Creators', text: 'color-accurate displays and enough GPU/memory for editing.' },
  { icon: 'briefcase', strong: 'Professionals', text: 'portability, battery life, and reliability.' },
  { icon: 'user', strong: 'Everyday users', text: 'a dependable laptop without needing to learn every spec.' },
];

export function AboutPage() {
  return (
    <SimplePageChrome>
      {/* HERO */}
      <section className="hero" style={{ paddingBottom: 'clamp(24px,3vh,40px)' }}>
        <div className="hero-field" aria-hidden="true">
          <div className="hero-orb hero-orb-a" />
          <div className="hero-orb hero-orb-b" />
          <div className="hero-grid" />
        </div>
        <div className="hero-inner">
          <span className="eyebrow-badge reveal">
            <LandingIcon name="sparkle" />
            About LaptopSathi AI
          </span>
          <h1>Making laptop decisions intelligent.</h1>
          <p className="lede">
            LaptopSathi is an AI-powered laptop decision platform designed to help people
            find, understand, compare, and choose laptops based on what actually matters
            to them.
          </p>
          <p className="hero-subline">Less specification overload. More clarity.</p>
        </div>
      </section>

      {/* WHAT IS LAPTOPSATHI */}
      <section className="band band-alt">
        <div className="section-head reveal">
          <span className="section-eyebrow">What it is</span>
          <h2>One platform, five things you get</h2>
        </div>
        <ul className="bullet-list reveal">
          {WHAT_IT_IS.map((w) => (
            <li key={w.strong}>
              <LandingIcon name="checkcircle" />
              <span><strong>{w.strong}</strong> — {w.text}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* HOW IT WORKS */}
      <section className="band">
        <div className="section-head reveal">
          <span className="section-eyebrow">How it works</span>
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

      {/* CORE CAPABILITIES */}
      <section className="band band-alt">
        <div className="section-head reveal">
          <span className="section-eyebrow">Core capabilities</span>
          <h2>What powers LaptopSathi?</h2>
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

      {/* WHO IT'S FOR */}
      <section className="band">
        <div className="section-head reveal">
          <span className="section-eyebrow">Who it&apos;s for</span>
          <h2>Built for very different kinds of buyers</h2>
        </div>
        <ul className="bullet-list reveal">
          {PERSONAS.map((p) => (
            <li key={p.strong}>
              <LandingIcon name={p.icon} />
              <span><strong>{p.strong}</strong> — {p.text}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* BUILT BY HARSH */}
      <section className="band band-alt">
        <div className="builtby-grid">
          <div className="builtby-logo reveal">
            <img src="/logo-full.png" alt="LaptopSathi AI" />
          </div>
          <div>
            <div className="section-head reveal">
              <span className="section-eyebrow">Who&apos;s behind this</span>
              <h2>Built with curiosity. Built by Harsh.</h2>
              <p>
                LaptopSathi is an independent project exploring how AI can make everyday
                technology decisions simpler and more understandable.
              </p>
            </div>
            <div className="builtby-panel reveal">
              <div className="builtby-name">Harsh Saxena</div>
              <div className="builtby-socials">
                {SOCIAL_LINKS.map(({ label, href, Icon }) => (
                  <a key={label} href={href} target="_blank" rel="noopener noreferrer" className="social-btn">
                    <Icon />
                    {label}
                    <LandingIcon name="arrowupright" className="go" />
                  </a>
                ))}
              </div>
              <p className="builtby-contact">
                For any queries or complaints, contact:{' '}
                <a href="mailto:harsh06srh@gmail.com">harsh06srh@gmail.com</a>
              </p>
            </div>
          </div>
        </div>
      </section>
    </SimplePageChrome>
  );
}
