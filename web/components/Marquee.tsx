"use client";

import { PROVIDERS } from "@/lib/site";

export function Marquee() {
  const row = [...PROVIDERS, ...PROVIDERS];
  return (
    <div className="fade-x relative w-full overflow-hidden">
      <div className="flex w-max animate-marquee items-center gap-10 py-1">
        {row.map((p, i) => (
          <span key={i} className="whitespace-nowrap text-sm font-medium text-ink-faint">
            {p}
          </span>
        ))}
      </div>
    </div>
  );
}
