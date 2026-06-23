"use client";

import { Container, Section, Eyebrow } from "./ui";
import { Reveal, Stagger, Item, ConicCard } from "./fx";

const pains = [
  {
    k: "01",
    t: "Your model changed and nobody told you",
    b: "Providers update what sits behind a stable name like gpt-4o-mini. Your fair hiring filter starts behaving differently overnight — no changelog, no alert.",
  },
  {
    k: "02",
    t: "Bias creeps in where logs can't see it",
    b: "Observability tools record what your model said. They can't tell you it scored two identical candidates differently because of age.",
  },
  {
    k: "03",
    t: "Procurement is already asking for proof",
    b: "Enterprise security teams send 200-line AI-governance questionnaires. Most startups have nothing to put in the box marked “bias monitoring.”",
  },
  {
    k: "04",
    t: "Doing it by hand costs €50k and months",
    b: "A manual readiness project means lawyers, consultants, and a DPIA you don’t have time to write — for a deadline that arrives on 2 August 2026.",
  },
];

export function Struggle() {
  return (
    <Section id="struggle" className="border-t border-line">
      <Container>
        <Reveal className="max-w-2xl">
          <Eyebrow>The current reality</Eyebrow>
          <h2 className="h-display text-4xl md:text-5xl">
            Right now, you <span className="text-ink-muted">can’t prove</span> your AI is fair.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-ink-muted">
            And the first time most teams find out is when a regulator, an enterprise buyer, or a journalist
            asks them to. The risk is invisible until it isn’t.
          </p>
        </Reveal>

        <Stagger className="mt-14 grid gap-5 md:grid-cols-2">
          {pains.map((p) => (
            <Item key={p.k}>
              <ConicCard className="h-full">
                <span className="font-mono text-sm text-brand-light">{p.k}</span>
                <h3 className="mt-3 text-xl font-semibold">{p.t}</h3>
                <p className="mt-2.5 leading-relaxed text-ink-muted">{p.b}</p>
              </ConicCard>
            </Item>
          ))}
        </Stagger>
      </Container>
    </Section>
  );
}
