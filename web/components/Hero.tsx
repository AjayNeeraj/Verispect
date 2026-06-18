"use client";

import { motion } from "framer-motion";
import { Container, Button, Arrow, Eyebrow, Gradient, openLead } from "./ui";
import { Marquee } from "./Marquee";

const ease = [0.16, 1, 0.3, 1] as const;

export function Hero() {
  return (
    <section className="relative overflow-hidden pb-20 pt-36 md:pb-28 md:pt-44">
      {/* aurora + grid backdrop */}
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-[-20%] h-[640px] w-[900px] -translate-x-1/2 rounded-full bg-brand/20 blur-[140px] animate-aurora" />
        <div className="absolute inset-0 grid-backdrop opacity-70" />
      </div>

      <Container className="flex flex-col items-center text-center">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease }}>
          <Eyebrow>EU AI Act · high-risk rules from 2 August 2026</Eyebrow>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 22, filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.85, ease, delay: 0.05 }}
          className="h-display max-w-4xl text-[44px] sm:text-6xl md:text-[72px]"
        >
          Prove your AI behaves.
          <br />
          <Gradient>Before anyone asks.</Gradient>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease, delay: 0.18 }}
          className="mt-7 max-w-2xl text-lg leading-relaxed text-ink-muted md:text-xl"
        >
          Automated EU AI Act compliance for high-risk AI — hiring, credit, insurance, legal.
          Verispect monitors your model for bias and drift and generates the audit-ready evidence,
          in <span className="text-ink">one line of code</span>. We never see your data.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease, delay: 0.3 }}
          className="mt-9 flex flex-col items-center gap-3 sm:flex-row"
        >
          <Button onClick={openLead}>
            Run my free AI Act Snapshot <Arrow />
          </Button>
          <Button variant="ghost" href="#how">
            See how it works
          </Button>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.45 }}
          className="mt-5 text-sm text-ink-faint"
        >
          🔒 Only hashes &amp; vectors leave your machine · 5-minute setup · no card
        </motion.p>

        {/* product visual */}
        <ProductCard />

        {/* provider strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="mt-16 w-full max-w-3xl"
        >
          <p className="mb-4 text-xs uppercase tracking-widest text-ink-faint">Works with every major model</p>
          <Marquee />
        </motion.div>
      </Container>
    </section>
  );
}

function ProductCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, rotateX: 12 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 1, ease, delay: 0.4 }}
      style={{ perspective: 1000 }}
      className="relative mt-16 w-full max-w-3xl"
    >
      <div className="glass overflow-hidden p-1.5 shadow-glow">
        <div className="rounded-xl bg-bg-soft/80 p-5 md:p-7">
          {/* top bar */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_2px_rgba(52,211,153,0.7)]" />
              <span className="text-sm font-medium">Monitoring Active</span>
            </div>
            <span className="font-mono text-xs text-ink-faint">acme-hr · gpt-4o-mini</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <Metric label="Compliance" value="86.3%" tone="good" />
            <Metric label="Drift events" value="11" tone="warn" />
            <Metric label="Avg drift" value="0.07" tone="good" />
          </div>

          {/* sparkline */}
          <div className="mt-6 rounded-lg border border-line bg-white/[0.015] p-4">
            <div className="mb-3 flex items-center justify-between text-xs text-ink-faint">
              <span>Behavioural drift · last 30 days</span>
              <span className="text-brand-light">Annex III §4 · Employment</span>
            </div>
            <Spark />
          </div>
        </div>
      </div>
      {/* glow base */}
      <div aria-hidden className="absolute -bottom-10 left-1/2 h-24 w-3/4 -translate-x-1/2 rounded-full bg-brand/30 blur-[60px]" />
    </motion.div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: "good" | "warn" }) {
  return (
    <div className="rounded-lg border border-line bg-white/[0.02] p-4 text-left">
      <p className="text-xs text-ink-faint">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${tone === "good" ? "text-emerald-300" : "text-amber-300"}`}>{value}</p>
    </div>
  );
}

function Spark() {
  const pts = [8, 10, 7, 9, 6, 12, 7, 5, 11, 8, 6, 9, 5, 7, 6, 4, 8, 5, 16, 7, 6, 5];
  const max = Math.max(...pts);
  const w = 560, h = 60, step = w / (pts.length - 1);
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${i * step} ${h - (p / max) * (h - 8)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-16 w-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#22D3EE" /><stop offset="0.5" stopColor="#3B82F6" /><stop offset="1" stopColor="#C026D3" />
        </linearGradient>
      </defs>
      <motion.path
        d={d} fill="none" stroke="url(#sg)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.6, delay: 0.9, ease: "easeInOut" }}
      />
      <circle cx={18 * step} cy={h - (16 / max) * (h - 8)} r="3.5" fill="#fbbf24" />
    </svg>
  );
}
