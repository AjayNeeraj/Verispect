"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Tilt } from "./fx";

type Phase = "scan" | "scored" | "flagged";
const SEQ: { p: Phase; ms: number }[] = [
  { p: "scan", ms: 2200 },
  { p: "scored", ms: 1500 },
  { p: "flagged", ms: 2600 },
];

export function BiasProbeDemo() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setI((v) => (v + 1) % SEQ.length), SEQ[i].ms);
    return () => clearTimeout(t);
  }, [i]);
  const phase = SEQ[i].p;
  const scored = phase !== "scan";
  const flagged = phase === "flagged";

  return (
    <Tilt max={6} className="relative w-full max-w-lg">
      <div className="glass relative overflow-hidden p-1.5 shadow-glow">
        <div className="relative rounded-xl bg-bg-soft/90 p-5">
          {/* header */}
          <div className="mb-5 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand/70" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand" />
              </span>
              <span className="text-sm font-medium">Live probe</span>
            </div>
            <span className="font-mono text-xs text-ink-faint">bias_age_01 · running</span>
          </div>

          {/* candidates */}
          <div className="relative space-y-3">
            {/* scan line */}
            <AnimatePresence>
              {phase === "scan" && (
                <motion.div
                  key={i}
                  className="pointer-events-none absolute inset-y-0 z-10 w-24"
                  initial={{ left: "-15%" }}
                  animate={{ left: "100%" }}
                  transition={{ duration: 2.2, ease: "easeInOut" }}
                  style={{ background: "linear-gradient(90deg, transparent, rgba(124,110,255,0.25), rgba(34,211,238,0.35), transparent)" }}
                />
              )}
            </AnimatePresence>

            <Row name="Alex Chen" age="26" score="7.0" flagged={false} reveal={scored} />
            <Row name="Alex Chen" age="54" score="6.0" flagged={flagged} reveal={scored} highlight={flagged} />
          </div>

          {/* verdict */}
          <div className="mt-5 h-[46px]">
            <AnimatePresence mode="wait">
              {flagged ? (
                <motion.div
                  key="flag"
                  initial={{ opacity: 0, y: 8, scale: 0.96 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: "spring", stiffness: 320, damping: 20 }}
                  className="flex items-center justify-between rounded-xl border border-amber-400/40 bg-amber-400/[0.08] px-4 py-3"
                >
                  <span className="flex items-center gap-2 text-sm font-medium text-amber-200">
                    <Spark /> Drift detected · age cited for 54, not 26
                  </span>
                  <span className="font-mono text-[11px] text-amber-200/70">sim 0.74</span>
                </motion.div>
              ) : (
                <motion.div
                  key="run"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="flex items-center gap-2 px-1 py-3 text-sm text-ink-faint"
                >
                  <span className="font-mono">{scored ? "scoring divergence…" : "probing identical profiles…"}</span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
      <div aria-hidden className="absolute -bottom-8 left-1/2 h-20 w-3/4 -translate-x-1/2 rounded-full bg-brand/30 blur-[55px]" />
    </Tilt>
  );
}

function Row({ name, age, score, flagged, reveal, highlight = false }: { name: string; age: string; score: string; flagged: boolean; reveal: boolean; highlight?: boolean }) {
  return (
    <div className={`flex items-center justify-between rounded-xl border px-4 py-3 transition-colors duration-500 ${highlight ? "border-amber-400/40 bg-amber-400/[0.05]" : "border-line bg-white/[0.02]"}`}>
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-full bg-brand-gradient opacity-80" />
        <div>
          <div className="text-sm font-medium">{name}</div>
          <div className="font-mono text-[11px] text-ink-faint">6 yrs · Python · team lead</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="rounded-md bg-white/[0.05] px-2 py-0.5 font-mono text-[11px] text-ink-muted">age {age}</span>
        <AnimatePresence>
          {reveal && (
            <motion.span
              initial={{ opacity: 0, scale: 0.6 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 400, damping: 22 }}
              className={`w-12 text-right text-xl font-semibold ${highlight ? "text-amber-300" : "text-emerald-300"}`}
            >
              {score}
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function Spark() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M8 1l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5z" fill="currentColor" />
    </svg>
  );
}
