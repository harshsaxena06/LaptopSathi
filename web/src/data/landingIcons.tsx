// Ported verbatim from landing-preview.html's inline ICONS map.
import React from 'react';

const ICON_MARKUP: Record<string, React.ReactNode> = {
  sparkle: (
    <path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" />
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="m21 21-4.3-4.3" />
    </>
  ),
  wallet: (
    <>
      <rect x="3" y="6" width="18" height="13" rx="2" />
      <path d="M3 10h18M16 14h2" />
    </>
  ),
  bulb: (
    <path d="M9 18h6M10 22h4M12 2a6 6 0 0 0-4 10.5c.6.55 1 1.36 1 2.2V16h6v-1.3c0-.84.4-1.65 1-2.2A6 6 0 0 0 12 2z" />
  ),
  compare: (
    <>
      <rect x="3" y="4" width="7" height="16" rx="1.5" />
      <rect x="14" y="4" width="7" height="16" rx="1.5" />
    </>
  ),
  sliders: (
    <>
      <path d="M4 6h6M14 6h6M4 12h11M19 12h1M4 18h3M11 18h9" />
      <circle cx="12" cy="6" r="2" />
      <circle cx="17" cy="12" r="2" />
      <circle cx="9" cy="18" r="2" />
    </>
  ),
  db: (
    <>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5" />
      <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
    </>
  ),
  gauge: (
    <>
      <path d="M4 18a8 8 0 1 1 16 0" />
      <path d="M12 18l3-5" />
    </>
  ),
  cpu: (
    <>
      <rect x="6" y="6" width="12" height="12" rx="2" />
      <rect x="9.5" y="9.5" width="5" height="5" />
      <path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3" />
    </>
  ),
  graduationcap: (
    <>
      <path d="M2 8.5 12 4l10 4.5-10 4.5-10-4.5z" />
      <path d="M6 10.6V15c0 1.7 2.7 3 6 3s6-1.3 6-3v-4.4" />
      <path d="M22 8.5v5.5" />
    </>
  ),
  code: (
    <>
      <path d="M8.5 7 3 12l5.5 5" />
      <path d="M15.5 7 21 12l-5.5 5" />
    </>
  ),
  gamepad: (
    <>
      <rect x="2" y="7" width="20" height="10" rx="5" />
      <path d="M6.5 9.5v4M4.5 11.5h4" />
      <circle cx="16" cy="10.5" r="1" />
      <circle cx="18.5" cy="13" r="1" />
    </>
  ),
  palette: (
    <>
      <path d="M12 3a9 9 0 1 0 0 18c1.1 0 2-.9 2-2 0-.5-.2-.9-.5-1.3-.3-.4-.5-.8-.5-1.2 0-1.1.9-2 2-2h2a4 4 0 0 0 4-4c0-4.4-4.4-7.5-9-7.5z" />
      <circle cx="7.3" cy="10.7" r="1" />
      <circle cx="9.8" cy="7" r="1" />
      <circle cx="14.5" cy="7.3" r="1" />
      <circle cx="17" cy="11" r="1" />
    </>
  ),
  briefcase: (
    <>
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M3 12.5h18" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
    </>
  ),
  checkcircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m8.3 12.4 2.4 2.4 5-5" />
    </>
  ),
  xcircle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m9 9 6 6M15 9l-6 6" />
    </>
  ),
  arrowupright: <path d="M7 17 17 7M8 7h9v9" />,
  chevrondown: <path d="m6 9 6 6 6-6" />,
};

export function LandingIcon({ name, ...props }: { name: string } & React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" {...props}>
      {ICON_MARKUP[name] ?? null}
    </svg>
  );
}

export function LandingStarIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 20 20" {...props}>
      <path d="M10 1.5l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L1.3 7.8l6.1-.7L10 1.5z" />
    </svg>
  );
}
