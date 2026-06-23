"use client";

import {
  motion, useInView, useScroll, useSpring, useMotionValue,
  useTransform, animate, type Variants,
} from "framer-motion";
import { useEffect, useRef, useState, type ReactNode, type MouseEvent } from "react";

const EASE = [0.22, 1, 0.36, 1] as const;

/* ── Film grain overlay — instant "premium" texture ───────────────────────── */
export function Grain() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[200] opacity-[0.045] mix-blend-soft-light"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
      }}
    />
  );
}

/* ── Scroll progress beam (top) ───────────────────────────────────────────── */
export function ScrollBeam() {
  const { scrollYProgress } = useScroll();
  const x = useSpring(scrollYProgress, { stiffness: 120, damping: 30, mass: 0.3 });
  return (
    <motion.div
      style={{ scaleX: x, transformOrigin: "0%" }}
      className="fixed inset-x-0 top-0 z-[300] h-[2px] bg-brand-gradient"
    />
  );
}

/* ── Living aurora mesh (multiple drifting blobs) ─────────────────────────── */
export function AuroraMesh() {
  const blobs = [
    { c: "rgba(124,110,255,0.28)", s: 620, x: "8%", y: "-8%", d: 18 },
    { c: "rgba(34,211,238,0.16)", s: 460, x: "70%", y: "4%", d: 24 },
    { c: "rgba(192,38,211,0.18)", s: 520, x: "48%", y: "18%", d: 21 },
  ];
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      {blobs.map((b, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-[120px]"
          style={{ width: b.s, height: b.s, left: b.x, top: b.y, background: b.c }}
          animate={{ x: [0, 40, -30, 0], y: [0, -30, 25, 0], scale: [1, 1.08, 0.96, 1] }}
          transition={{ duration: b.d, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}

/* ── Headline that reveals per word (blur + rise + clip) ───────────────────── */
export function WordsReveal({ text, className = "", delay = 0 }: { text: string; className?: string; delay?: number }) {
  const words = text.split(" ");
  return (
    <span className={className}>
      {words.map((w, i) => (
        <span key={i} className="inline-block overflow-hidden align-bottom" style={{ paddingBottom: "0.08em" }}>
          <motion.span
            className="inline-block"
            initial={{ y: "110%", opacity: 0, filter: "blur(8px)" }}
            animate={{ y: "0%", opacity: 1, filter: "blur(0px)" }}
            transition={{ duration: 0.85, ease: EASE, delay: delay + i * 0.06 }}
          >
            {w}&nbsp;
          </motion.span>
        </span>
      ))}
    </span>
  );
}

/* ── Reveal (clip-mask wipe, not the generic fade) ────────────────────────── */
const clipUp: Variants = {
  hidden: { opacity: 0, y: 28, clipPath: "inset(0 0 12% 0)", filter: "blur(4px)" },
  show: { opacity: 1, y: 0, clipPath: "inset(0 0 0% 0)", filter: "blur(0px)", transition: { duration: 0.8, ease: EASE } },
};
export function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-90px" });
  return (
    <motion.div ref={ref} variants={clipUp} initial="hidden" animate={inView ? "show" : "hidden"} transition={{ delay }} className={className}>
      {children}
    </motion.div>
  );
}
export function Stagger({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-90px" });
  return (
    <motion.div ref={ref} initial="hidden" animate={inView ? "show" : "hidden"} variants={{ show: { transition: { staggerChildren: 0.1 } } }} className={className}>
      {children}
    </motion.div>
  );
}
export function Item({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <motion.div variants={clipUp} className={className}>{children}</motion.div>;
}

/* ── Count-up number ──────────────────────────────────────────────────────── */
export function CountUp({ to, suffix = "", decimals = 0, className = "" }: { to: number; suffix?: string; decimals?: number; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const controls = animate(0, to, {
      duration: 1.4, ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setVal(v),
    });
    return () => controls.stop();
  }, [inView, to]);
  return <span ref={ref} className={className}>{val.toFixed(decimals)}{suffix}</span>;
}

/* ── Magnetic button wrapper ──────────────────────────────────────────────── */
export function Magnetic({ children, strength = 0.35 }: { children: ReactNode; strength?: number }) {
  const x = useMotionValue(0); const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 220, damping: 18 });
  const sy = useSpring(y, { stiffness: 220, damping: 18 });
  function onMove(e: MouseEvent<HTMLSpanElement>) {
    const r = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * strength);
    y.set((e.clientY - (r.top + r.height / 2)) * strength);
  }
  return (
    <motion.span style={{ x: sx, y: sy, display: "inline-block" }} onMouseMove={onMove} onMouseLeave={() => { x.set(0); y.set(0); }}>
      {children}
    </motion.span>
  );
}

/* ── Conic-border card (Linear/Vercel signature) ──────────────────────────── */
export function ConicCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`group relative overflow-hidden rounded-2xl p-px ${className}`}>
      <div
        aria-hidden
        className="absolute -inset-[150%] opacity-0 transition-opacity duration-500 group-hover:opacity-100"
        style={{
          background: "conic-gradient(from 0deg, transparent 0deg, #7C6EFF 60deg, #22D3EE 110deg, transparent 180deg)",
          animation: "spin 5s linear infinite",
        }}
      />
      <div className="relative h-full rounded-[15px] border border-line bg-bg-surface/80 p-6 backdrop-blur-sm">
        {children}
      </div>
    </div>
  );
}

/* ── Subtle 3D tilt wrapper ───────────────────────────────────────────────── */
export function Tilt({ children, className = "", max = 8 }: { children: ReactNode; className?: string; max?: number }) {
  const rx = useMotionValue(0); const ry = useMotionValue(0);
  const srx = useSpring(rx, { stiffness: 150, damping: 18 });
  const sry = useSpring(ry, { stiffness: 150, damping: 18 });
  function onMove(e: MouseEvent<HTMLDivElement>) {
    const r = e.currentTarget.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    ry.set(px * max); rx.set(-py * max);
  }
  return (
    <motion.div
      onMouseMove={onMove}
      onMouseLeave={() => { rx.set(0); ry.set(0); }}
      style={{ rotateX: srx, rotateY: sry, transformPerspective: 1200 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
