"use client";

import { motion, useInView, type Variants } from "framer-motion";
import { useRef, type ReactNode, type MouseEvent } from "react";

/* ---------- layout ---------- */
export function Container({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`container-x ${className}`}>{children}</div>;
}

export function Section({ id, children, className = "" }: { id?: string; children: ReactNode; className?: string }) {
  return (
    <section id={id} className={`relative py-24 md:py-32 ${className}`}>
      {children}
    </section>
  );
}

/* ---------- text ---------- */
export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <span className="pill mb-6">
      <span className="h-1.5 w-1.5 rounded-full bg-brand shadow-[0_0_10px_2px_rgba(124,110,255,0.8)]" />
      {children}
    </span>
  );
}

export function Gradient({ children }: { children: ReactNode }) {
  return <span className="text-gradient">{children}</span>;
}

/* ---------- scroll reveal ---------- */
const up: Variants = {
  hidden: { opacity: 0, y: 22, filter: "blur(6px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } },
};

export function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      variants={up}
      initial="hidden"
      animate={inView ? "show" : "hidden"}
      transition={{ delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function Stagger({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={inView ? "show" : "hidden"}
      variants={{ show: { transition: { staggerChildren: 0.09 } } }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function Item({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <motion.div variants={up} className={className}>
      {children}
    </motion.div>
  );
}

/* ---------- CTA: opens the lead modal anywhere via a window event ---------- */
export function openLead() {
  if (typeof window !== "undefined") window.dispatchEvent(new CustomEvent("open-lead"));
}

export function Button({
  children,
  variant = "primary",
  onClick,
  href,
  className = "",
}: {
  children: ReactNode;
  variant?: "primary" | "ghost";
  onClick?: () => void;
  href?: string;
  className?: string;
}) {
  const base =
    "group relative inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-[15px] font-semibold transition-all duration-200 will-change-transform active:scale-[0.98]";
  const styles =
    variant === "primary"
      ? "bg-brand text-white shadow-[0_8px_30px_-8px_rgba(124,110,255,0.7)] hover:bg-brand-glow hover:-translate-y-0.5"
      : "border border-line bg-white/[0.02] text-ink hover:border-brand/60 hover:bg-brand/[0.06]";
  const cls = `${base} ${styles} ${className}`;
  if (href) return <a href={href} className={cls}>{children}</a>;
  return <button type="button" onClick={onClick} className={cls}>{children}</button>;
}

export function Arrow() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="transition-transform group-hover:translate-x-0.5">
      <path d="M3 8h9m0 0L8.5 4.5M12 8l-3.5 3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ---------- spotlight card (hover-follow glow) ---------- */
export function SpotlightCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  function onMove(e: MouseEvent<HTMLDivElement>) {
    const el = e.currentTarget;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--x", `${e.clientX - r.left}px`);
    el.style.setProperty("--y", `${e.clientY - r.top}px`);
  }
  return (
    <div onMouseMove={onMove} className={`card-spot group p-6 ${className}`}>
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{ background: "radial-gradient(280px circle at var(--x) var(--y), rgba(124,110,255,0.14), transparent 60%)" }}
      />
      <div className="relative">{children}</div>
    </div>
  );
}
