import React from 'react';

type IconProps = React.SVGProps<SVGSVGElement>;

const base = {
  width: 18,
  height: 18,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
};

export const EyeIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

export const EyeOffIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M17.9 17.9A10.9 10.9 0 0 1 12 19c-7 0-11-7-11-7a19.9 19.9 0 0 1 4.7-5.6M9.9 4.2A10.4 10.4 0 0 1 12 4c7 0 11 7 11 7a19.6 19.6 0 0 1-2.3 3.2" />
    <path d="M14.1 14.1a3 3 0 1 1-4.2-4.2" />
    <path d="M1 1l22 22" />
  </svg>
);

export const CheckIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M20 6L9 17l-5-5" />
  </svg>
);

export const ShieldIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-4z" />
  </svg>
);

export const SunIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </svg>
);

export const MoonIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z" />
  </svg>
);

export const ArrowLeftIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M19 12H5M12 19l-7-7 7-7" />
  </svg>
);

export const GoogleIcon = (props: IconProps) => (
  <svg width="16" height="16" viewBox="0 0 24 24" {...props}>
    <path
      fill="currentColor"
      d="M21.6 12.23c0-.7-.06-1.38-.18-2.03H12v3.85h5.4a4.62 4.62 0 0 1-2 3.03v2.5h3.24c1.9-1.75 3-4.32 3-7.35z"
    />
    <path
      fill="currentColor"
      d="M12 22c2.7 0 4.97-.9 6.63-2.42l-3.24-2.5c-.9.6-2.05.96-3.4.96-2.6 0-4.8-1.76-5.6-4.12H3.05v2.58A10 10 0 0 0 12 22z"
    />
    <path fill="currentColor" d="M6.4 13.92a6 6 0 0 1 0-3.84V7.5H3.05a10 10 0 0 0 0 9l3.35-2.58z" />
    <path
      fill="currentColor"
      d="M12 5.96c1.47 0 2.8.5 3.84 1.5l2.87-2.87A9.6 9.6 0 0 0 12 2a10 10 0 0 0-8.95 5.5l3.35 2.58c.8-2.36 3-4.12 5.6-4.12z"
    />
  </svg>
);

export const GithubIcon = (props: IconProps) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M12 .5a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2.1c-3.3.7-4-1.6-4-1.6-.5-1.4-1.3-1.8-1.3-1.8-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .5z" />
  </svg>
);

export const LinkedinIcon = (props: IconProps) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.03-1.85-3.03-1.85 0-2.14 1.45-2.14 2.94v5.66H9.34V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.61 0 4.28 2.38 4.28 5.47v6.27zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z" />
  </svg>
);

export const HomeIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M3 11l9-7 9 7" /><path d="M5 10v10h14V10" />
  </svg>
);
export const SearchIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
  </svg>
);
export const SparkleIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M12 3l1.8 4.9L19 9.5l-5.2 1.6L12 16l-1.8-4.9L5 9.5l5.2-1.6L12 3z" />
  </svg>
);
export const ColumnsIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <rect x="3" y="4" width="5" height="16" rx="1" /><rect x="9.5" y="4" width="5" height="16" rx="1" /><rect x="16" y="4" width="5" height="16" rx="1" />
  </svg>
);
export const WalletIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <rect x="3" y="6" width="18" height="13" rx="2" /><path d="M3 10h18" /><circle cx="16.5" cy="14.5" r="1" />
  </svg>
);
export const BookmarkIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M6 3h12v18l-6-4-6 4V3z" />
  </svg>
);
export const ChartIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M4 20V10M12 20V4M20 20v-7" />
  </svg>
);
export const UserIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
  </svg>
);
export const PlusIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M12 5v14M5 12h14" />
  </svg>
);
export const StarIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.9 6.6 19.5l1.2-6-4.5-4.2 6.1-.7L12 3z" />
  </svg>
);
export const AlertIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16h.01" />
  </svg>
);
export const InboxIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M4 12h4l2 3h4l2-3h4" /><path d="M4 12l1.5-7h13L20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6z" />
  </svg>
);
export const CloseIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M18 6L6 18M6 6l12 12" />
  </svg>
);
export const GaugeIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M4 18a8 8 0 1 1 16 0" /><path d="M12 18l3-5" />
  </svg>
);
export const DatabaseIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <ellipse cx="12" cy="5" rx="8" ry="3" />
    <path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5" />
    <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
  </svg>
);
export const UploadIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M12 16V4M7 9l5-5 5 5" /><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </svg>
);
export const RefreshIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M3 12a9 9 0 0 1 15.3-6.4L21 8M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-15.3 6.4L3 16M3 21v-5h5" />
  </svg>
);
export const SettingsIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06A2 2 0 1 1 7.04 4.3l.06.06A1.65 1.65 0 0 0 8.92 4.7h.09A1.65 1.65 0 0 0 10 3.09V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);
export const TerminalIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M4 17l6-5-6-5" /><path d="M12 19h8" />
  </svg>
);
export const PanelLeftIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <rect x="3" y="4" width="18" height="16" rx="2.5" />
    <path d="M9 4v16" />
  </svg>
);
export const MailIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" />
  </svg>
);
export const LockIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <rect x="4" y="10" width="16" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" />
  </svg>
);
export const LightbulbIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M9 18h6M10 22h4M12 2a6 6 0 0 0-4 10.5c.6.55 1 1.36 1 2.2V16h6v-1.3c0-.84.4-1.65 1-2.2A6 6 0 0 0 12 2z" />
  </svg>
);
export const SlidersIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M4 6h6M14 6h6M4 12h11M19 12h1M4 18h3M11 18h9" />
    <circle cx="12" cy="6" r="2" /><circle cx="17" cy="12" r="2" /><circle cx="9" cy="18" r="2" />
  </svg>
);
export const ExternalLinkIcon = (props: IconProps) => (
  <svg {...base} {...props}>
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <path d="M15 3h6v6M10 14L21 3" />
  </svg>
);
