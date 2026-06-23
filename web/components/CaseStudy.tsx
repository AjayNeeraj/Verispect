"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { Container, Section, Eyebrow } from "./ui";
import { Reveal, CountUp } from "./fx";

export function CaseStudy() {
  return (
    <Section id="evidence" className="border-t border-line">
      <Container>
        <div className="grid items-center gap-14 lg:grid-cols-2">
          <Reveal>
            <Eyebrow>Real finding · reproducible</Eyebrow>
            <h2 className="h-display text-4xl md:text-5xl">
              Two identical CVs.
              <br />
              Different scores.
            </h2>
            <p className="mt-6 text-lg leading-relaxed text-ink-muted">
              On our very first calibration run, a mainstream model rated two candidates with{" "}
              <span className="text-ink">identical résumés</span> — same experience, same skills — differently.
              It cited <span className="text-ink">age</span> as a factor for the 54-year-old, and not for the
              26-year-old.
            </p>
            <p className="mt-4 text-lg leading-relaxed text-ink-muted">
              That bias is running in production hiring and lending systems across Europe right now. Verispect
              is the instrument that catches it — measured, scored, and reproducible.
            </p>

            <div className="mt-8 grid grid-cols-3 gap-4">
              <Stat n={<CountUp to={0.74} decimals={2} />} l="similarity (medium)" />
              <Stat n={<CountUp to={8} />} l="protected categories" />
              <Stat n={<CountUp to={100} suffix="%" />} l="reproducible scores" />
            </div>
          </Reveal>

          {/* visual: paired probe */}
          <Reveal delay={0.1}>
            <div className="glass p-6">
              <div className="grid grid-cols-2 gap-4">
                <CandidateCard name="Alex Chen" age="26" score="7.0" tone="neutral" note="No age factor mentioned." />
                <CandidateCard name="Alex Chen" age="54" score="6.0" tone="flag" note="“…age may be a consideration.”" />
              </div>

              <div className="mt-5 flex items-center justify-between rounded-xl border border-amber-400/30 bg-amber-400/[0.06] px-4 py-3">
                <span className="text-sm font-medium text-amber-200">Divergence detected · age</span>
                <span className="font-mono text-xs text-amber-200/80">EV-2026-0528-031</span>
              </div>
              <p className="mt-4 text-center text-xs text-ink-faint">
                Identical profile · one demographic signal changed · a fair model gives equivalent answers.
              </p>
            </div>
          </Reveal>
        </div>
      </Container>
    </Section>
  );
}

function Stat({ n, l }: { n: ReactNode; l: string }) {
  return (
    <div>
      <div className="text-3xl font-semibold text-gradient">{n}</div>
      <div className="mt-1 text-xs leading-snug text-ink-faint">{l}</div>
    </div>
  );
}

function CandidateCard({ name, age, score, tone, note }: { name: string; age: string; score: string; tone: "neutral" | "flag"; note: string }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className={`rounded-xl border p-4 ${tone === "flag" ? "border-amber-400/40 bg-amber-400/[0.04]" : "border-line bg-white/[0.02]"}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{name}</span>
        <span className="rounded-md bg-white/[0.05] px-2 py-0.5 font-mono text-xs text-ink-muted">age {age}</span>
      </div>
      <div className={`mt-3 text-3xl font-semibold ${tone === "flag" ? "text-amber-300" : "text-ink"}`}>{score}<span className="text-base text-ink-faint">/10</span></div>
      <p className="mt-2 text-xs leading-snug text-ink-muted">{note}</p>
    </motion.div>
  );
}
