"use client";

import { Container, Section, Eyebrow, Gradient } from "./ui";
import { Reveal, Stagger, Item, ConicCard } from "./fx";
import { CAPABILITIES } from "@/lib/site";

const steps = [
  { n: "1", t: "Add one line", b: "Wrap your existing client. Zero added latency — your calls return immediately; all our work runs in the background.", code: 'client = wrap(OpenAI(...),\n  verispect_key="vs_live_…")' },
  { n: "2", t: "We interrogate it", b: "Calibrated probes fire at your live model on a sample of traffic, scoring bias and drift against your baseline — deterministically." },
  { n: "3", t: "You get the proof", b: "A continuously-updated, article-mapped audit pack. Hand it to a regulator or an enterprise buyer the moment they ask." },
];

export function Transformation() {
  return (
    <Section id="how" className="border-t border-line">
      <Container>
        <Reveal className="mx-auto max-w-2xl text-center">
          <div className="flex justify-center"><Eyebrow>The transformation</Eyebrow></div>
          <h2 className="h-display text-4xl md:text-5xl">
            From blind to <Gradient>audit-ready</Gradient> in a day.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-ink-muted">
            One line connects it. From then on, Verispect is your autonomous AI compliance department —
            running 24/7, generating the evidence for you.
          </p>
        </Reveal>

        {/* steps */}
        <Stagger className="mt-16 grid gap-5 md:grid-cols-3">
          {steps.map((s) => (
            <Item key={s.n}>
              <div className="card-spot h-full p-6">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-white font-semibold shadow-[0_8px_24px_-8px_rgba(124,110,255,0.8)]">
                  {s.n}
                </div>
                <h3 className="text-xl font-semibold">{s.t}</h3>
                <p className="mt-2.5 leading-relaxed text-ink-muted">{s.b}</p>
                {s.code && (
                  <pre className="mt-4 overflow-x-auto rounded-lg border border-line bg-bg p-3 font-mono text-[12.5px] leading-relaxed text-brand-light">
{s.code}
                  </pre>
                )}
              </div>
            </Item>
          ))}
        </Stagger>

        {/* capability bento */}
        <Reveal className="mt-20">
          <h3 className="text-center text-sm uppercase tracking-widest text-ink-faint">Your compliance department, on autopilot</h3>
        </Reveal>
        <Stagger className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {CAPABILITIES.map((c) => (
            <Item key={c.title}>
              <ConicCard className="h-full">
                <div className="mb-3 h-8 w-8 rounded-lg bg-brand-gradient opacity-90" />
                <h4 className="font-semibold">{c.title}</h4>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{c.body}</p>
              </ConicCard>
            </Item>
          ))}
        </Stagger>
      </Container>
    </Section>
  );
}
