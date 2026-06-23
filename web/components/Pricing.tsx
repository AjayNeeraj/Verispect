"use client";

import { Container, Section, Eyebrow, Gradient, Button, Arrow, openLead } from "./ui";
import { Reveal, Stagger, Item } from "./fx";
import { PRICING } from "@/lib/site";

function Check() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="mt-0.5 shrink-0">
      <path d="M3.5 8.5l3 3 6-7" stroke="#34D399" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Pricing() {
  return (
    <Section id="pricing" className="border-t border-line">
      <Container>
        <Reveal className="mx-auto max-w-2xl text-center">
          <div className="flex justify-center"><Eyebrow>The offer</Eyebrow></div>
          <h2 className="h-display text-4xl md:text-5xl">
            Priced like a SaaS seat. <br className="hidden sm:block" />
            <Gradient>Worth a compliance department.</Gradient>
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-ink-muted">
            AI Act fines reach €15M or 3% of global turnover. A manual readiness project costs €50k+ and months.
            There is no cheap tier — only free (strategic) and premium.
          </p>
        </Reveal>

        <Stagger className="mt-14 grid gap-5 lg:grid-cols-4">
          {PRICING.map((p) => (
            <Item key={p.name}>
              <div
                className={`relative flex h-full flex-col rounded-2xl border p-6 ${
                  p.highlight
                    ? "border-brand/50 bg-gradient-to-b from-brand/[0.10] to-transparent shadow-glow"
                    : "border-line bg-bg-surface/60"
                }`}
              >
                {p.tag && (
                  <span className={`absolute right-5 top-5 rounded-full px-2.5 py-1 text-[11px] font-medium ${p.highlight ? "bg-brand text-white" : "border border-line text-ink-faint"}`}>
                    {p.tag}
                  </span>
                )}
                <h3 className="text-lg font-semibold">{p.name}</h3>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-4xl font-semibold tracking-tight">{p.price}</span>
                </div>
                <span className="mt-1 text-sm text-ink-faint">{p.cadence}</span>
                <p className="mt-4 text-sm leading-relaxed text-ink-muted">{p.desc}</p>

                <ul className="mt-5 flex flex-1 flex-col gap-2.5">
                  {p.features.map((f) => (
                    <li key={f} className="flex gap-2 text-sm text-ink-muted">
                      <Check /> {f}
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={openLead}
                  variant={p.highlight ? "primary" : "ghost"}
                  className="mt-6 w-full"
                >
                  {p.cta} {p.highlight && <Arrow />}
                </Button>
              </div>
            </Item>
          ))}
        </Stagger>

        <Reveal className="mt-8 text-center">
          <p className="text-sm text-ink-faint">
            🛡️ Run the free snapshot first — only join if it shows you something worth fixing. Cancel anytime, no lock-in.
            <br className="hidden sm:block" />
            Verispect provides compliance evidence and monitoring, not legal advice or certification. You remain the operator.
          </p>
        </Reveal>
      </Container>
    </Section>
  );
}
