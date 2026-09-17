import React from 'react';

interface VasudhaLogoProps {
  variant?: 'full' | 'icon' | 'wordmark' | 'sidebar';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  theme?: 'dark' | 'light';
  className?: string;
  showTagline?: boolean;
}

/**
 * Official VASUDHA Logo & Wordmark
 * Faithful vector rendering of the globe-and-leaf emblem and custom flared typography
 * with the signature leaf accent in the 'A's.
 */
export const VasudhaLogo: React.FC<VasudhaLogoProps> = ({
  variant = 'full',
  size = 'md',
  theme = 'light',
  className = '',
  showTagline = true,
}) => {
  const isDark = theme === 'dark';

  // Dimension scaling
  const iconDimensions = {
    sm: 28,
    md: 40,
    lg: 64,
    xl: 88,
  }[size];

  // Colors
  const primaryTextColor = isDark ? '#f2f5f3' : '#142a22';
  const subtitleColor = isDark ? '#98b0a5' : '#1b3b30';
  const leafColor = isDark ? '#4ade80' : '#4d7c5f';

  /* --- 1. THE EMBLEM: Globe + Sweeping Leaf + Water/Soil Waves --- */
  const Emblem = ({ sizePx }: { sizePx: number }) => {
    const idSuffix = React.useId().replace(/:/g, '');
    const leafGradId = `leafGrad-${idSuffix}`;
    const globeGradId = `globeGrad-${idSuffix}`;
    const waveGradId = `waveGrad-${idSuffix}`;

    return (
      <svg
        width={sizePx}
        height={sizePx}
        viewBox="0 0 160 160"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform duration-200"
      >
        <defs>
          {/* Rich Leaf Gradient (forest to emerald) */}
          <linearGradient id={leafGradId} x1="20" y1="140" x2="80" y2="20" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#2e6b52' : '#163b2c'} />
            <stop offset="50%" stopColor={isDark ? '#40916c' : '#22543d'} />
            <stop offset="100%" stopColor={isDark ? '#52b788' : '#2f6d50'} />
          </linearGradient>

          {/* Continents Fill */}
          <linearGradient id={globeGradId} x1="60" y1="30" x2="110" y2="100" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#94d2bd' : '#184232'} />
            <stop offset="100%" stopColor={isDark ? '#52b788' : '#133527'} />
          </linearGradient>

          {/* Bottom Wave Gradients */}
          <linearGradient id={waveGradId} x1="40" y1="100" x2="130" y2="130" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#2d6a4f' : '#1b4332'} />
            <stop offset="100%" stopColor={isDark ? '#52b788' : '#2d6a4f'} />
          </linearGradient>
        </defs>

        {/* Outer Circular Boundary (fine ring, open at upper left where leaf ascends) */}
        <path
          d="M 66 22 A 62 62 0 1 1 120 128"
          stroke={isDark ? '#88b59e' : '#193f30'}
          strokeWidth="3.2"
          strokeLinecap="round"
          fill="none"
          opacity={isDark ? 0.85 : 0.9}
        />

        {/* Continents of the Earth (Stylized Eurasia, South Asia, Australia & Archipelagos) */}
        <g fill={`url(#${globeGradId})`}>
          {/* Main Eurasian / Indian Landmass */}
          <path d="M 72 42 C 78 36, 88 38, 98 40 C 104 42, 112 47, 114 54 C 115 59, 108 64, 104 68 C 98 72, 94 76, 92 84 C 91 87, 88 88, 86 86 C 84 83, 85 78, 87 74 C 88 70, 85 68, 81 69 C 76 71, 74 66, 76 60 C 77 56, 73 52, 70 48 Z" />
          {/* Subcontinent / Peninsula protrusion */}
          <path d="M 87 68 C 89 74, 91 80, 89 83 C 86 84, 85 80, 84 76 Z" />
          {/* East Asia & Japan arc */}
          <path d="M 112 56 C 115 57, 118 62, 116 66 C 114 68, 111 65, 110 60 Z" />
          <path d="M 119 63 C 120 65, 121 68, 119 70 C 117 71, 116 67, 118 64 Z" />
          {/* Southeast Asian Island chain */}
          <path d="M 103 80 C 106 80, 107 83, 104 84 C 101 84, 101 81, 103 80 Z" />
          <path d="M 107 84 C 110 84, 111 87, 108 88 C 106 88, 106 85, 107 84 Z" />
          <path d="M 113 87 C 116 87, 117 90, 114 91 C 112 91, 112 88, 113 87 Z" />
          {/* Australia / Oceania */}
          <path d="M 108 97 C 114 94, 122 96, 124 102 C 126 108, 120 115, 114 115 C 108 115, 105 108, 106 103 C 107 99, 106 98, 108 97 Z" />
        </g>

        {/* Sweeping Botanical Leaf (Wraps up the left quadrant) */}
        <path
          d="M 52 120 C 44 105, 36 84, 40 58 C 43 42, 52 30, 60 20 C 64 26, 68 34, 69 44 C 71 58, 64 80, 56 96 C 53 103, 50 110, 48 116 Z"
          fill={`url(#${leafGradId})`}
        />
        {/* Subtle leaf central vein highlight */}
        <path
          d="M 42 108 C 45 88, 50 64, 58 35"
          stroke={isDark ? '#86efac' : '#34d399'}
          strokeWidth="1.2"
          strokeLinecap="round"
          opacity="0.65"
        />

        {/* Lower Contour Waves / Flowing River & Soil Terraces */}
        {/* Upper wave */}
        <path
          d="M 45 116 C 60 110, 80 110, 100 120 C 114 127, 128 126, 136 122 C 128 129, 112 134, 96 128 C 76 120, 58 124, 48 130 Z"
          fill={`url(#${waveGradId})`}
        />
        {/* Lower wave cradling bottom base */}
        <path
          d="M 52 132 C 68 126, 88 126, 106 136 C 118 142, 128 140, 134 136 C 124 145, 106 148, 92 142 C 74 135, 58 138, 52 144 Z"
          fill={`url(#${leafGradId})`}
        />
      </svg>
    );
  };

  /* --- 2. BESPOKE 'VASUDHA' WORDMARK WITH LEAF IN BOTH 'A's --- */
  const WordmarkText = ({ heightPx }: { heightPx: number }) => {
    return (
      <svg
        height={heightPx}
        viewBox="0 0 460 70"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="overflow-visible"
        aria-label="VASUDHA"
      >
        {/* V */}
        <path
          d="M 15 12 L 28 12 L 52 56 L 76 12 L 89 12 L 59 64 L 45 64 Z"
          fill={primaryTextColor}
        />
        {/* V serifs / flared tips */}
        <path d="M 12 12 L 28 12 L 28 15 L 12 15 Z" fill={primaryTextColor} />
        <path d="M 76 12 L 92 12 L 92 15 L 76 15 Z" fill={primaryTextColor} />

        {/* A (First) with Leaf Accent */}
        {/* Outer diagonal legs */}
        <path
          d="M 110 64 L 132 14 L 144 14 L 166 64 L 153 64 L 147 48 L 129 48 L 123 64 Z M 134 38 L 142 38 L 138 24 Z"
          fill={primaryTextColor}
        />
        {/* The Signature Leaf inside 'A' */}
        <path
          d="M 138 48 C 134 43, 133 35, 138 26 C 143 35, 142 43, 138 48 Z"
          fill={leafColor}
        />
        <path
          d="M 138 48 L 138 28"
          stroke={isDark ? '#86efac' : '#1b4332'}
          strokeWidth="0.8"
          strokeLinecap="round"
        />

        {/* S */}
        <path
          d="M 230 22 C 226 15, 216 12, 203 12 C 188 12, 178 20, 178 30 C 178 41, 188 45, 204 49 C 220 53, 228 57, 228 66 C 228 77, 216 83, 201 83 C 185 83, 174 76, 171 65 L 183 63 C 185 71, 192 75, 201 75 C 210 75, 217 71, 217 64 C 217 56, 209 52, 193 48 C 178 44, 168 39, 168 28 C 168 18, 178 12, 192 12 C 204 12, 214 17, 218 25 Z"
          transform="matrix(0.85 0 0 0.85 24 -1)"
          fill={primaryTextColor}
        />

        {/* U */}
        <path
          d="M 238 14 L 250 14 L 250 46 C 250 58, 259 65, 271 65 C 283 65, 292 58, 292 46 L 292 14 L 304 14 L 304 46 C 304 64, 290 73, 271 73 C 252 73, 238 64, 238 46 Z"
          transform="matrix(0.9 0 0 0.9 14 0)"
          fill={primaryTextColor}
        />

        {/* D */}
        <path
          d="M 298 13 L 324 13 C 344 13, 357 23, 357 38.5 C 357 54, 344 64, 324 64 L 298 64 Z M 310 21 L 310 56 L 323 56 C 337 56, 345 49, 345 38.5 C 345 28, 337 21, 323 21 Z"
          fill={primaryTextColor}
        />

        {/* H */}
        <path
          d="M 370 13 L 382 13 L 382 34 L 406 34 L 406 13 L 418 13 L 418 64 L 406 64 L 406 42 L 382 42 L 382 64 L 370 64 Z"
          fill={primaryTextColor}
        />

        {/* A (Second) with Leaf Accent */}
        <path
          d="M 426 64 L 448 14 L 460 14 L 482 64 L 469 64 L 463 48 L 445 48 L 439 64 Z M 450 38 L 458 38 L 454 24 Z"
          transform="translate(-3, 0)"
          fill={primaryTextColor}
        />
        {/* The Signature Leaf inside second 'A' */}
        <path
          d="M 451 48 C 447 43, 446 35, 451 26 C 456 35, 455 43, 451 48 Z"
          fill={leafColor}
        />
        <path
          d="M 451 48 L 451 28"
          stroke={isDark ? '#86efac' : '#1b4332'}
          strokeWidth="0.8"
          strokeLinecap="round"
        />
      </svg>
    );
  };

  /* --- RENDER MODES --- */

  // 1. Sidebar variant: Compact horizontal layout (Emblem + text stacked)
  if (variant === 'sidebar') {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <Emblem sizePx={34} />
        <div className="flex flex-col">
          <span
            className="font-serif tracking-[0.2em] font-bold text-sm leading-none"
            style={{ color: primaryTextColor }}
          >
            VASUDHA
          </span>
          <span
            className="text-[10px] tracking-wider uppercase font-sans font-medium mt-1"
            style={{ color: subtitleColor }}
          >
            Biodiversity Intelligence
          </span>
        </div>
      </div>
    );
  }

  // 2. Icon only
  if (variant === 'icon') {
    return (
      <div className={`inline-flex items-center justify-center ${className}`}>
        <Emblem sizePx={iconDimensions} />
      </div>
    );
  }

  // 3. Wordmark only
  if (variant === 'wordmark') {
    return (
      <div className={`flex flex-col items-center text-center ${className}`}>
        <WordmarkText heightPx={size === 'lg' ? 44 : 32} />
        {showTagline && (
          <p
            className="text-xs sm:text-sm font-sans tracking-wide font-medium mt-2"
            style={{ color: subtitleColor }}
          >
            Biodiversity Intelligence for a Living Earth
          </p>
        )}
      </div>
    );
  }

  // 4. Full Hero Variant (Centered: Large Emblem, Wordmark, Tagline)
  return (
    <div className={`flex flex-col items-center text-center select-none ${className}`}>
      {/* Centered Large Emblem */}
      <div className="relative mb-3 flex items-center justify-center">
        <Emblem sizePx={iconDimensions} />
      </div>

      {/* Bespoke Wordmark with leaf in both 'A's */}
      <div className="w-full max-w-[280px] sm:max-w-[340px] flex justify-center">
        <WordmarkText heightPx={size === 'xl' ? 38 : size === 'lg' ? 34 : 26} />
      </div>

      {/* Official Tagline */}
      {showTagline && (
        <p
          className="text-xs sm:text-sm font-sans font-medium tracking-wide mt-2"
          style={{ color: subtitleColor }}
        >
          Biodiversity Intelligence for a Living Earth
        </p>
      )}
    </div>
  );
};
