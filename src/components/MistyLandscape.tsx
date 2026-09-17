import React from 'react';

/**
 * MistyLandscape: Atmospheric watercolor landscape of rolling green hills,
 * a winding river, and soft botanical silhouettes matching the Vasudha aesthetic.
 */
export const MistyLandscape: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      className={`pointer-events-none select-none absolute bottom-0 left-0 right-0 w-full overflow-hidden h-[240px] sm:h-[300px] ${className}`}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 1440 400"
        preserveAspectRatio="none"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full object-cover"
      >
        <defs>
          {/* Top blend fade so mountains emerge softly from mist */}
          <linearGradient id="skyMist" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f7f8f5" stopOpacity="1" />
            <stop offset="35%" stopColor="#f7f8f5" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#f7f8f5" stopOpacity="0" />
          </linearGradient>

          {/* Far hills gradient */}
          <linearGradient id="farHills" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#e3ede5" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#d3e2d6" stopOpacity="0.9" />
          </linearGradient>

          {/* Mid hills gradient */}
          <linearGradient id="midHills" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c3d8c8" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#a9c4b0" stopOpacity="0.95" />
          </linearGradient>

          {/* Near hills gradient */}
          <linearGradient id="nearHills" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8fae96" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#6d9176" stopOpacity="0.98" />
          </linearGradient>

          {/* River gradient */}
          <linearGradient id="riverGrad" x1="720" y1="180" x2="720" y2="400" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#eef5f1" stopOpacity="0.9" />
            <stop offset="60%" stopColor="#dbe9df" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#c8ddd0" stopOpacity="0.7" />
          </linearGradient>

          {/* Botanical foliage tone */}
          <linearGradient id="foliageGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#557a5e" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#3c5f46" stopOpacity="0.95" />
          </linearGradient>
        </defs>

        {/* 1. Distant Mountain Ridges */}
        <path
          d="M 0 170 C 180 130, 360 180, 520 150 C 680 120, 840 160, 1020 130 C 1200 110, 1340 140, 1440 160 L 1440 400 L 0 400 Z"
          fill="url(#farHills)"
        />

        {/* 2. Mid Rolling Terraces & Ridge */}
        <path
          d="M 0 220 C 160 190, 320 230, 480 200 C 640 170, 780 220, 940 190 C 1100 160, 1280 210, 1440 230 L 1440 400 L 0 400 Z"
          fill="url(#midHills)"
        />

        {/* 3. Winding River Valley */}
        <path
          d="M 720 180 C 700 230, 750 270, 700 320 C 660 360, 680 390, 710 400 L 790 400 C 760 380, 780 350, 740 310 C 790 260, 740 220, 760 180 Z"
          fill="url(#riverGrad)"
        />

        {/* 4. Foreground Terraced Hills (Left and Right) */}
        <path
          d="M 0 280 C 200 250, 420 280, 620 330 C 660 340, 680 370, 680 400 L 0 400 Z"
          fill="url(#nearHills)"
        />
        <path
          d="M 1440 270 C 1260 250, 1060 280, 860 330 C 820 340, 800 370, 800 400 L 1440 400 Z"
          fill="url(#nearHills)"
        />

        {/* 5. Left Foreground Botanical Sprig / Leaves */}
        <g fill="url(#foliageGrad)">
          {/* Main stem */}
          <path d="M 0 400 C 40 360, 90 320, 140 290 L 143 293 C 94 323, 44 363, 0 404 Z" />
          {/* Leaflets along the branch */}
          <path d="M 45 370 C 35 345, 55 330, 75 340 C 65 355, 55 365, 45 370 Z" />
          <path d="M 80 340 C 70 315, 95 305, 110 320 C 100 335, 90 340, 80 340 Z" />
          <path d="M 115 315 C 105 290, 130 280, 145 295 C 135 308, 125 315, 115 315 Z" />
          <path d="M 140 290 C 135 265, 160 260, 172 272 C 160 285, 150 290, 140 290 Z" />
          {/* Lower accent leaves */}
          <path d="M 20 390 C 25 360, 50 360, 55 380 C 45 390, 30 395, 20 390 Z" />
        </g>

        {/* 6. Right Foreground Botanical Grass / Fern Sprig */}
        <g fill="url(#foliageGrad)">
          <path d="M 1440 390 C 1390 350, 1340 330, 1290 310 C 1310 335, 1350 365, 1390 395 Z" />
          <path d="M 1360 345 C 1385 325, 1410 340, 1395 360 C 1380 355, 1370 350, 1360 345 Z" />
          <path d="M 1310 325 C 1335 305, 1360 320, 1345 340 C 1330 335, 1320 330, 1310 325 Z" />
          <path d="M 1400 380 C 1420 355, 1440 365, 1435 385 Z" />
        </g>

        {/* Atmospheric mist wash overlay */}
        <rect x="0" y="0" width="1440" height="240" fill="url(#skyMist)" />
      </svg>
    </div>
  );
};
