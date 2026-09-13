import React from 'react';
import { motion } from 'framer-motion';

/** A small original, abstract "AI laptop" illustration — a stylised laptop
 * with a glowing screen and orbiting nodes representing recommendation /
 * search signals. Built entirely from primitive shapes, no external assets. */
export function AuthIllustration() {
  return (
    <svg
      width="100%"
      height="220"
      viewBox="0 0 360 220"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Illustration of a laptop with AI recommendation nodes"
    >
      <defs>
        <linearGradient id="screenGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0.05" />
        </linearGradient>
        <linearGradient id="baseGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="var(--border-strong)" />
          <stop offset="100%" stopColor="var(--border)" />
        </linearGradient>
      </defs>

      {/* orbiting signal nodes */}
      {[
        { cx: 60, cy: 60, r: 5, delay: 0 },
        { cx: 300, cy: 50, r: 4, delay: 0.4 },
        { cx: 320, cy: 130, r: 6, delay: 0.8 },
        { cx: 40, cy: 140, r: 4, delay: 1.2 },
      ].map((n, i) => (
        <motion.circle
          key={i}
          cx={n.cx}
          cy={n.cy}
          r={n.r}
          fill="var(--accent)"
          opacity={0.7}
          animate={{ opacity: [0.3, 0.9, 0.3], scale: [1, 1.3, 1] }}
          transition={{ duration: 2.4, repeat: Infinity, delay: n.delay, ease: 'easeInOut' }}
        />
      ))}

      {/* connecting lines */}
      <path d="M60 60 L140 90" stroke="var(--border-strong)" strokeWidth="1" strokeDasharray="3 4" />
      <path d="M300 50 L220 85" stroke="var(--border-strong)" strokeWidth="1" strokeDasharray="3 4" />
      <path d="M320 130 L245 110" stroke="var(--border-strong)" strokeWidth="1" strokeDasharray="3 4" />
      <path d="M40 140 L115 115" stroke="var(--border-strong)" strokeWidth="1" strokeDasharray="3 4" />

      {/* laptop screen */}
      <rect x="110" y="40" width="140" height="94" rx="10" fill="var(--panel)" stroke="var(--border-strong)" strokeWidth="2" />
      <rect x="122" y="52" width="116" height="70" rx="4" fill="url(#screenGrad)" />
      {/* screen "content" bars, representing scores/results */}
      {[0, 1, 2].map((i) => (
        <motion.rect
          key={i}
          x={132}
          y={64 + i * 18}
          width={40 + i * 22}
          height={8}
          rx={4}
          fill="var(--accent)"
          opacity={0.55}
          animate={{ width: [40 + i * 22, 60 + i * 18, 40 + i * 22] }}
          transition={{ duration: 3, repeat: Infinity, delay: i * 0.3, ease: 'easeInOut' }}
        />
      ))}

      {/* laptop base */}
      <path d="M92 150 L268 150 L282 172 L78 172 Z" fill="url(#baseGrad)" />
      <rect x="150" y="150" width="60" height="4" rx="2" fill="var(--bg)" opacity="0.4" />

      {/* soft ground shadow */}
      <ellipse cx="180" cy="184" rx="110" ry="8" fill="var(--accent)" opacity="0.06" />
    </svg>
  );
}
