import React from "react";

interface BrandMarkProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: {
    container: "h-8 w-8",
    svg: "h-5 w-5",
    title: "text-sm",
    subtitle: "text-[9px]",
  },
  md: {
    container: "h-10 w-10",
    svg: "h-7 w-7",
    title: "text-base",
    subtitle: "text-[10px]",
  },
  lg: {
    container: "h-12 w-12",
    svg: "h-8 w-8",
    title: "text-xl",
    subtitle: "text-[11px]",
  },
};

export function BrandMark({ size = "md", className = "" }: BrandMarkProps) {
  const currentSize = sizeMap[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Pixel-art Academic Globe containing S.S. (Warm Institutional Palette) */}
      <div
        className={`flex shrink-0 items-center justify-center border border-[#E8D8BD] bg-[#3B2921] shadow-xs ${currentSize.container}`}
        style={{ borderRadius: "3px" }}
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 32 32"
          className={currentSize.svg}
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          shapeRendering="crispEdges"
        >
          {/* Globe Boundary Pixels */}
          <rect x="10" y="2" width="12" height="2" fill="#FFF8E7" />
          <rect x="6" y="4" width="4" height="2" fill="#FFF8E7" />
          <rect x="22" y="4" width="4" height="2" fill="#FFF8E7" />
          <rect x="4" y="6" width="2" height="4" fill="#FFF8E7" />
          <rect x="26" y="6" width="2" height="4" fill="#FFF8E7" />
          <rect x="2" y="10" width="2" height="12" fill="#FFF8E7" />
          <rect x="28" y="10" width="2" height="12" fill="#FFF8E7" />
          <rect x="4" y="22" width="2" height="4" fill="#FFF8E7" />
          <rect x="26" y="22" width="2" height="4" fill="#FFF8E7" />
          <rect x="6" y="26" width="4" height="2" fill="#FFF8E7" />
          <rect x="22" y="26" width="4" height="2" fill="#FFF8E7" />
          <rect x="10" y="28" width="12" height="2" fill="#FFF8E7" />

          {/* Meridian / Graticule Markers */}
          <rect x="15" y="4" width="2" height="4" fill="#E8A317" />
          <rect x="15" y="24" width="2" height="4" fill="#E8A317" />
          <rect x="4" y="15" width="4" height="2" fill="#E8D8BD" />
          <rect x="24" y="15" width="4" height="2" fill="#E8D8BD" />

          {/* S.S. Pixel Monogram */}
          {/* First 'S' */}
          <rect x="9" y="11" width="5" height="2" fill="#D96B27" />
          <rect x="9" y="13" width="2" height="1" fill="#D96B27" />
          <rect x="9" y="14" width="5" height="2" fill="#D96B27" />
          <rect x="12" y="16" width="2" height="1" fill="#D96B27" />
          <rect x="9" y="17" width="5" height="2" fill="#D96B27" />

          {/* Center Divider Dot */}
          <rect x="15" y="17" width="2" height="2" fill="#E8A317" />

          {/* Second 'S' */}
          <rect x="18" y="11" width="5" height="2" fill="#D96B27" />
          <rect x="18" y="13" width="2" height="1" fill="#D96B27" />
          <rect x="18" y="14" width="5" height="2" fill="#D96B27" />
          <rect x="21" y="16" width="2" height="1" fill="#D96B27" />
          <rect x="18" y="17" width="5" height="2" fill="#D96B27" />
        </svg>
      </div>

      {/* Institutional Typography Lockup */}
      <div className="flex flex-col leading-tight">
        <span
          className={`font-serif font-bold tracking-tight text-[#3B2921] ${currentSize.title}`}
        >
          STUDENT SPHERE
        </span>
        <span
          className={`font-semibold uppercase tracking-wider text-[#6B5A4A] ${currentSize.subtitle}`}
        >
          Academic Portal &amp; Management System
        </span>
      </div>
    </div>
  );
}