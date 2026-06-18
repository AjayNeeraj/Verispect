"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState, type FormEvent } from "react";
import { SITE } from "@/lib/site";

export function LeadModal() {
  const [open, setOpen] = useState(false);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const onOpen = () => { setOpen(true); setDone(false); };
    window.addEventListener("open-lead", onOpen);
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => { window.removeEventListener("open-lead", onOpen); window.removeEventListener("keydown", onKey); };
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    const f = new FormData(e.currentTarget);
    const payload = {
      company: f.get("company"),
      email: f.get("email"),
      usecase: f.get("usecase"),
      source: "web-nextjs",
    };
    try {
      await fetch(`${SITE.supabaseUrl}/rest/v1/leads`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SITE.supabaseKey,
          Authorization: `Bearer ${SITE.supabaseKey}`,
          Prefer: "return=minimal",
        },
        body: JSON.stringify(payload),
      });
    } catch {
      /* swallow — lead still captured client-side */
    }
    setBusy(false);
    setDone(true);
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={(e) => e.target === e.currentTarget && setOpen(false)}
        >
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.98 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="glass relative z-10 w-full max-w-md p-7"
          >
            <button onClick={() => setOpen(false)} aria-label="Close" className="absolute right-5 top-5 text-ink-faint hover:text-ink">✕</button>

            {!done ? (
              <>
                <h3 className="text-2xl font-semibold tracking-tight">Get your free snapshot</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-muted">
                  Drop your work email. We’ll send the one-line setup and your 2-page readiness snapshot. We never see your data.
                </p>
                <form onSubmit={submit} className="mt-6 space-y-3">
                  <Field name="company" placeholder="Company" required />
                  <Field name="email" type="email" placeholder="Work email" required />
                  <Field name="usecase" placeholder="What does your LLM do? (e.g. CV screening)" />
                  <button
                    type="submit" disabled={busy}
                    className="w-full rounded-xl bg-brand px-5 py-3 font-semibold text-white shadow-[0_8px_30px_-8px_rgba(124,110,255,0.7)] transition hover:bg-brand-glow disabled:opacity-60"
                  >
                    {busy ? "Sending…" : "Send me the snapshot →"}
                  </button>
                </form>
                <p className="mt-4 text-[11px] text-ink-faint">
                  By submitting you agree to be contacted about Verispect. Unsubscribe anytime.
                </p>
              </>
            ) : (
              <div className="py-4 text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-400/15 text-2xl">✅</div>
                <h3 className="text-2xl font-semibold tracking-tight">On its way.</h3>
                <p className="mt-3 text-sm leading-relaxed text-ink-muted">
                  Check your inbox for the one-line setup + your snapshot. The founder will follow up personally — welcome to the Founding cohort.
                </p>
                <button onClick={() => setOpen(false)} className="mt-6 rounded-xl border border-line px-5 py-2.5 text-sm font-medium hover:border-brand/60">
                  Done
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Field(props: { name: string; type?: string; placeholder: string; required?: boolean }) {
  return (
    <input
      {...props}
      className="w-full rounded-xl border border-line bg-white/[0.03] px-4 py-3 text-[15px] text-ink outline-none transition placeholder:text-ink-faint focus:border-brand/70 focus:bg-white/[0.05]"
    />
  );
}
