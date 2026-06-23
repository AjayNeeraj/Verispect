"use client";

import { motion } from "framer-motion";
import { Container, Button, Arrow, Eyebrow, openLead } from "./ui";
import { AuroraMesh, WordsReveal, Magnetic } from "./fx";
import { BiasProbeDemo } from "./BiasProbeDemo";
import { Marquee } from "./Marquee";

const EASE = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section className="relative overflow-hidden pb-24 pt-36 md:pt-40">
      <AuroraMesh />
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 grid-backdrop opacity-60" />

      <Container className="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
        {/* left: copy */}
        <div className="text-center lg:text-left">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="flex justify-center lg:justify-start">
            <Eyebrow>EU AI Act · high-risk rules from 2 Aug 2026</Eyebrow>
          </motion.div>

          <h1 className="h-display mt-6 text-[42px] leading-[1.02] sm:text-6xl lg:text-[64px]">
            <WordsReveal text="Prove your AI behaves." />
            <br />
            <span className="text-gradient">
              <WordsReveal text="Before anyone asks." delay={0.4} />
            </span>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: EASE, delay: 0.7 }}
            className="mx-auto mt-7 max-w-xl text-lg leading-relaxed text-ink-muted lg:mx-0"
          >
            Automated EU AI Act compliance for high-risk AI. Verispect interrogates your live model for
            bias and drift and writes the audit-ready evidence — in{" "}
            <span className="text-ink">one line of code</span>. We never see your data.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: EASE, delay: 0.85 }}
            className="mt-9 flex flex-col items-center gap-3 sm:flex-row lg:justify-start"
          >
            <Magnetic>
              <Button onClick={openLead}>Run my free AI Act Snapshot <Arrow /></Button>
            </Magnetic>
            <Button variant="ghost" href="#how">See how it works</Button>
          </motion.div>

          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1, duration: 0.7 }} className="mt-5 text-sm text-ink-faint">
            🔒 Only hashes &amp; vectors leave your machine · 5-min setup · no card
          </motion.p>
        </div>

        {/* right: live product */}
        <motion.div
          initial={{ opacity: 0, x: 30, filter: "blur(8px)" }}
          animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
          transition={{ duration: 1, ease: EASE, delay: 0.5 }}
          className="flex justify-center lg:justify-end"
        >
          <BiasProbeDemo />
        </motion.div>
      </Container>

      {/* provider marquee */}
      <Container className="mt-20">
        <p className="mb-4 text-center text-xs uppercase tracking-[0.2em] text-ink-faint">Works with every major model</p>
        <Marquee />
      </Container>
    </section>
  );
}
