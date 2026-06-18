"use client";

import { useEffect, useState } from "react";
import { Container, Button, openLead } from "./ui";

const links = [
  { label: "The problem", href: "#struggle" },
  { label: "How it works", href: "#how" },
  { label: "Evidence", href: "#evidence" },
  { label: "Pricing", href: "#pricing" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        scrolled ? "border-b border-line bg-bg/70 backdrop-blur-xl" : "border-b border-transparent"
      }`}
    >
      <Container className="flex h-[72px] items-center justify-between">
        <a href="#" className="flex items-center gap-3" aria-label="Verispect">
          <img src="/logo-mark.svg" alt="" width={40} height={40} className="drop-shadow-[0_0_12px_rgba(124,110,255,0.45)]" />
          <span className="text-[19px] font-semibold tracking-tight">
            Veri<span className="text-brand-light">spect</span>
          </span>
        </a>

        <nav className="hidden items-center gap-8 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm text-ink-muted transition-colors hover:text-ink">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={openLead} className="hidden text-sm font-medium text-ink-muted transition-colors hover:text-ink sm:block">
            Sign in
          </button>
          <Button onClick={openLead} className="!px-4 !py-2.5 !text-sm">
            Free snapshot
          </Button>
        </div>
      </Container>
    </header>
  );
}
