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
 * Precision-crafted vector identity featuring the celestial globe-and-leaf emblem
 * and bespoke flared typography with botanical leaf accents inside the 'A's.
 */
export const VasudhaLogo: React.FC<VasudhaLogoProps> = ({
  variant = 'full',
  size = 'md',
  theme = 'light',
  className = '',
  showTagline = true,
}) => {
  const isDark = theme === 'dark';

  // Scaled dimensions
  const iconDimensions = {
    sm: 28,
    md: 40,
    lg: 64,
    xl: 84,
  }[size];

  // Dynamic Theme Palette
  const primaryTextColor = isDark ? '#f4f7f5' : '#142a22';
  const subtitleColor = isDark ? '#a3b8ad' : '#3d594c';
  const leafAccentColor = isDark ? '#4ade80' : '#2e7d56';
  const leafVeinColor = isDark ? '#bbf7d0' : '#164e34';

  /* --- 1. THE EMBLEM: Living Earth, Orbiting Leaf & Hydrological Waves --- */
  const Emblem = ({ sizePx }: { sizePx: number }) => {
    const idSuffix = React.useId().replace(/[^a-zA-Z0-9]/g, '');
    const leafGradId = `leafGrad-${idSuffix}`;
    const globeGradId = `globeGrad-${idSuffix}`;
    const waveGradId = `waveGrad-${idSuffix}`;
    const ringGradId = `ringGrad-${idSuffix}`;

    return (
      <svg
        width={sizePx}
        height={sizePx}
        viewBox="0 0 160 160"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform duration-300 hover:scale-[1.02]"
        aria-hidden="true"
      >
        <defs>
          {/* Botanical Leaf Gradient */}
          <linearGradient id={leafGradId} x1="24" y1="136" x2="72" y2="18" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#164e34' : '#123326'} />
            <stop offset="45%" stopColor={isDark ? '#2e7d56' : '#1e543e'} />
            <stop offset="100%" stopColor={isDark ? '#52b788' : '#2e7d56'} />
          </linearGradient>

          {/* Continents / Biome Landmass Fill */}
          <linearGradient id={globeGradId} x1="56" y1="32" x2="114" y2="108" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#74c69d' : '#1a4332'} />
            <stop offset="100%" stopColor={isDark ? '#40916c' : '#123326'} />
          </linearGradient>

          {/* Hydrological & Soil Strata Waves */}
          <linearGradient id={waveGradId} x1="36" y1="104" x2="132" y2="136" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#1b4332' : '#173b2d'} />
            <stop offset="50%" stopColor={isDark ? '#2d6a4f' : '#22543d'} />
            <stop offset="100%" stopColor={isDark ? '#52b788' : '#2d6a4f'} />
          </linearGradient>

          {/* Orbital Circle Ring Gradient */}
          <linearGradient id={ringGradId} x1="60" y1="20" x2="140" y2="130" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={isDark ? '#52b788' : '#2d6a4f'} stopOpacity="0.3" />
            <stop offset="50%" stopColor={isDark ? '#74c69d' : '#193f30'} stopOpacity="0.9" />
            <stop offset="100%" stopColor={isDark ? '#95d5b2' : '#133527'} stopOpacity="0.95" />
          </linearGradient>
        </defs>

        {/* Outer Circular Celestial Boundary (fine ring, open where the botanical leaf ascends) */}
        <path
          d="M 64 22 A 62 62 0 1 1 126 126"
          stroke={`url(#${ringGradId})`}
          strokeWidth="3.4"
          strokeLinecap="round"
          fill="none"
        />

        {/* Global Continental Landmasses */}
        <g fill={`url(#${globeGradId})`}>
          {/* Eurasia & South Asian subcontinent */}
          <path d="M 72 40 C 78 34, 89 36, 99 38 C 105 40, 113 45, 115 52 C 116 58, 109 63, 105 67 C 99 71, 95 75, 93 83 C 92 86, 89 87, 87 85 C 85 82, 86 77, 88 73 C 89 69, 86 67, 82 68 C 77 70, 75 65, 77 59 C 78 55, 74 51, 71 47 Z" />
          {/* Indian Peninsula & Sri Lanka */}
          <path d="M 88 67 C 90 73, 92 79, 90 82 C 87 83, 86 79, 85 75 Z" />
          <circle cx="91.5" cy="88" r="1.8" />
          {/* East Asia & Japan Archipelago */}
          <path d="M 113 54 C 116 55, 119 60, 117 64 C 115 66, 112 63, 111 58 Z" />
          <path d="M 120 62 C 121 64, 122 67, 120 69 C 118 70, 117 66, 119 63 Z" />
          {/* Southeast Asian Archipelago */}
          <circle cx="104" cy="82" r="2.2" />
          <circle cx="109" cy="86" r="2" />
          <circle cx="115" cy="89" r="2.4" />
          {/* Oceania & Australia */}
          <path d="M 107 97 C 113 94, 121 96, 123 101 C 125 107, 119 114, 113 114 C 107 114, 104 107, 105 102 C 106 99, 105 98, 107 97 Z" />
        </g>

        {/* Sweeping Botanical Leaf (Wraps elegantly up the western quadrant) */}
        <path
          d="M 50 120 C 42 105, 34 84, 38 58 C 41 42, 50 30, 58 20 C 62 26, 66 34, 67 44 C 69 58, 62 80, 54 96 C 51 103, 48 110, 46 116 Z"
          fill={`url(#${leafGradId})`}
        />
        {/* Leaf central spine highlight */}
        <path
          d="M 40 108 C 43 88, 48 64, 56 35"
          stroke={isDark ? '#86efac' : '#34d399'}
          strokeWidth="1.4"
          strokeLinecap="round"
          opacity="0.75"
        />

        {/* Lower Hydrological Waves / River Flow & Soil Contours */}
        {/* Upper wave ribbon */}
        <path
          d="M 44 116 C 59 110, 79 110, 99 120 C 113 127, 127 126, 135 122 C 127 129, 111 134, 95 128 C 75 120, 57 124, 47 130 Z"
          fill={`url(#${waveGradId})`}
        />
        {/* Lower wave ribbon */}
        <path
          d="M 51 132 C 67 126, 87 126, 105 136 C 117 142, 127 140, 133 136 C 123 145, 105 148, 91 142 C 73 135, 57 138, 51 144 Z"
          fill={`url(#${leafGradId})`}
        />
      </svg>
    );
  };

  /* --- 2. THE WORDMARK: Precision Geometric & Flared Typography --- */
  const WordmarkText = ({ heightPx }: { heightPx: number }) => {
    return (
      <svg
        height={heightPx}
        viewBox="0 0 520 76"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="overflow-visible"
        aria-label="VASUDHA"
        role="img"
      >
        {/* === V === */}
        <path
          d="M 22 14 L 38 14 L 62 58 L 86 14 L 102 14 L 70 66 L 54 66 Z"
          fill={primaryTextColor}
        />
        {/* V Serifs */}
        <path d="M 18 14 L 38 14 L 38 17 L 18 17 Z" fill={primaryTextColor} />
        <path d="M 86 14 L 106 14 L 106 17 L 86 17 Z" fill={primaryTextColor} />

        {/* === A (First) with Botanical Leaf === */}
        <path
          d="M 124 66 L 148 14 L 162 14 L 186 66 L 171 66 L 164 49 L 146 49 L 139 66 Z M 151 38 L 159 38 L 155 24 Z"
          fill={primaryTextColor}
        />
        {/* Bottom flares on A */}
        <path d="M 120 66 L 142 66 L 142 63 L 120 63 Z" fill={primaryTextColor} />
        <path d="M 168 66 L 190 66 L 190 63 L 168 63 Z" fill={primaryTextColor} />
        {/* Leaf Accent inside A */}
        <path
          d="M 155 49 C 150 43, 149 35, 155 25 C 161 35, 160 43, 155 49 Z"
          fill={leafAccentColor}
        />
        <path
          d="M 155 49 L 155 27"
          stroke={leafVeinColor}
          strokeWidth="1"
          strokeLinecap="round"
        />

        {/* === S === */}
        <path
          d="M 252 23 C 248 16, 237 13, 223 13 C 206 13, 195 22, 195 33 C 195 44, 206 48, 223 52 C 240 56, 248 60, 248 70 C 248 81, 235 87, 219 87 C 202 87, 190 79, 187 67 L 200 65 C 202 74, 210 78, 219 78 C 229 78, 236 74, 236 67 C 236 58, 227 54, 211 50 C 195 46, 184 41, 184 29 C 184 18, 195 12, 210 12 C 223 12, 234 17, 238 26 Z"
          transform="matrix(0.86 0 0 0.86 38 -1)"
          fill={primaryTextColor}
        />

        {/* === U === */}
        <path
          d="M 264 14 L 277 14 L 277 47 C 277 59, 287 66, 300 66 C 313 66, 323 59, 323 47 L 323 14 L 336 14 L 336 47 C 336 66, 321 75, 300 75 C 279 75, 264 66, 264 47 Z"
          transform="matrix(0.9 0 0 0.9 28 0)"
          fill={primaryTextColor}
        />
        {/* U top serifs */}
        <path d="M 262 14 L 280 14 L 280 17 L 262 17 Z" fill={primaryTextColor} />
        <path d="M 318 14 L 336 14 L 336 17 L 318 17 Z" fill={primaryTextColor} />

        {/* === D === */}
        <path
          d="M 346 14 L 374 14 C 395 14, 409 25, 409 40 C 409 55, 395 66, 374 66 L 346 66 Z M 359 23 L 359 57 L 373 57 C 387 57, 396 49, 396 40 C 396 31, 387 23, 373 23 Z"
          fill={primaryTextColor}
        />
        {/* D serifs */}
        <path d="M 342 14 L 362 14 L 362 17 L 342 17 Z" fill={primaryTextColor} />
        <path d="M 342 66 L 362 66 L 362 63 L 342 63 Z" fill={primaryTextColor} />

        {/* === H === */}
        <path
          d="M 420 14 L 433 14 L 433 35 L 458 35 L 458 14 L 471 14 L 471 66 L 458 66 L 458 44 L 433 44 L 433 66 L 420 66 Z"
          fill={primaryTextColor}
        />
        {/* H serifs */}
        <path d="M 416 14 L 436 14 L 436 17 L 416 17 Z" fill={primaryTextColor} />
        <path d="M 416 66 L 436 66 L 436 63 L 416 63 Z" fill={primaryTextColor} />
        <path d="M 455 14 L 475 14 L 475 17 L 455 17 Z" fill={primaryTextColor} />
        <path d="M 455 66 L 475 66 L 475 63 L 455 63 Z" fill={primaryTextColor} />

        {/* === A (Second) with Botanical Leaf === */}
        <path
          d="M 482 66 L 506 14 L 520 14 L 544 66 L 529 66 L 522 49 L 504 49 L 497 66 Z M 509 38 L 517 38 L 513 24 Z"
          transform="translate(-3, 0)"
          fill={primaryTextColor}
        />
        {/* Bottom flares on second A */}
        <path d="M 475 66 L 497 66 L 497 63 L 475 63 Z" fill={primaryTextColor} />
        <path d="M 523 66 L 545 66 L 545 63 L 523 63 Z" fill={primaryTextColor} />
        {/* Leaf Accent inside second A */}
        <path
          d="M 510 49 C 505 43, 504 35, 510 25 C 516 35, 515 43, 510 49 Z"
          fill={leafAccentColor}
        />
        <path
          d="M 510 49 L 510 27"
          stroke={leafVeinColor}
          strokeWidth="1"
          strokeLinecap="round"
        />
      </svg>
    );
  };

  /* --- 3. RENDER VARIANTS --- */

  // 1. Sidebar variant: Compact horizontal lockup
  if (variant === 'sidebar') {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <Emblem sizePx={36} />
        <div className="flex flex-col">
          <span
            className="font-serif tracking-[0.22em] font-bold text-[15px] leading-none text-white"
            style={{ fontFamily: "'Cinzel', Georgia, serif" }}
          >
            VASUDHA
          </span>
          <span
            className="text-[10px] tracking-[0.14em] uppercase font-sans font-semibold mt-1 text-[#9cb5a8]"
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
            className="text-xs sm:text-sm font-sans tracking-wide font-medium mt-2.5"
            style={{ color: subtitleColor }}
          >
            Biodiversity Intelligence for a Living Earth
          </p>
        )}
      </div>
    );
  }

  // 4. Full Hero Variant (Centered: Large Emblem, Precision Wordmark, Tagline)
  return (
    <div className={`flex flex-col items-center text-center select-none ${className}`}>
      {/* Centered Emblem */}
      <div className="relative mb-3.5 flex items-center justify-center drop-shadow-xs">
        <Emblem sizePx={iconDimensions} />
      </div>

      {/* Precision Wordmark with Leaf Motif in both 'A's */}
      <div className="w-full max-w-[290px] sm:max-w-[360px] flex justify-center">
        <WordmarkText heightPx={size === 'xl' ? 38 : size === 'lg' ? 34 : 26} />
      </div>

      {/* Official Tagline */}
      {showTagline && (
        <p
          className="text-xs sm:text-sm font-sans font-medium tracking-wide mt-2.5"
          style={{ color: subtitleColor }}
        >
          Biodiversity Intelligence for a Living Earth
        </p>
      )}
    </div>
  );
};
