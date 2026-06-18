"use client";

import { useEffect, useState } from "react";
import { Container, Section, Button, Arrow, Gradient, openLead } from "./ui";
import { SITE } from "@/lib/site";

function useCountdown(iso: string) {
  const [days, setDays] = useState<number | null>(null);
  useEffect(() => {
    const tick = () => {
      const diff = new Date(iso).getTime() - Date.now();
      setDays(Math.max(0, Math.ceil(diff / 86400000)));
    };
    tick();
    const id = setInterval(tick, 60_000);
    return () => clearInterval(id);
  }, [iso]);
  return days;
}

export function FinalCTA() {
  const days = useCountdown(SITE.deadline);
  return (
    <Section className="border-t border-line">
      <Container>
        <div className="relative overflow-hidden rounded-3xl border border-brand/30 bg-bg-surface/60 px-6 py-16 text-center md:px-16 md:py-24">
          <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
            <div className="absolute left-1/2 top-[-40%] h-[420px] w-[700px] -translate-x-1/2 rounded-full bg-brand/20 blur-[120px]" />
            <div className="absolute inset-0 grid-backdrop opacity-50" />
          </div>

          <p className="font-mono text-sm text-brand-light">
            {days !== null ? `${days} days to 2 August 2026` : "Counting down to 2 August 2026"}
          </p>
          <h2 className="h-display mx-auto mt-5 max-w-3xl text-4xl md:text-6xl">
            The deadline is coming. <br />
            <Gradient>The proof shouldn’t.</Gradient>
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-ink-muted">
            See if your model is drifting in five minutes. One line of code, no card, and we never see your data.
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button onClick={openLead}>
              Run my free AI Act Snapshot <Arrow />
            </Button>
            <Button variant="ghost" href="#pricing">See pricing</Button>
          </div>
        </div>
      </Container>
    </Section>
  );
}
