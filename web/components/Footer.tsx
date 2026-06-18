import { Container } from "./ui";

export function Footer() {
  return (
    <footer className="border-t border-line py-14">
      <Container>
        <div className="flex flex-col items-start justify-between gap-10 md:flex-row">
          <div className="max-w-sm">
            <div className="flex items-center gap-3">
              <img src="/logo-mark.svg" alt="" width={36} height={36} />
              <span className="text-lg font-semibold tracking-tight">Veri<span className="text-brand-light">spect</span></span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-ink-muted">
              Verify + Inspect. Active AI behavioural assurance and EU AI Act evidence — in one line of code.
            </p>
            <p className="mt-4 text-sm text-ink-faint">hello@verispectai.com</p>
          </div>

          <div className="grid grid-cols-2 gap-x-16 gap-y-8 sm:grid-cols-3">
            <FooterCol title="Product" links={[["How it works", "#how"], ["Evidence", "#evidence"], ["Pricing", "#pricing"]]} />
            <FooterCol title="Company" links={[["LinkedIn", "https://www.linkedin.com/company/verispect-ai/"], ["The deadline", "#"], ["Contact", "mailto:hello@verispectai.com"]]} />
            <FooterCol title="Trust" links={[["Privacy", "#"], ["Security", "#"], ["DPA", "#"]]} />
          </div>
        </div>

        <div className="mt-12 border-t border-line pt-6">
          <p className="text-xs leading-relaxed text-ink-faint">
            Verispect provides AI behaviour monitoring and compliance evidence — not legal advice or certification; the operator remains responsible.
            EU AI Act high-risk obligations apply from 2 August 2026 (standalone Annex III may move to 2 December 2027 if the Digital Omnibus is adopted).
            © {new Date().getFullYear()} Verispect.
          </p>
        </div>
      </Container>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <h4 className="text-sm font-semibold">{title}</h4>
      <ul className="mt-4 space-y-3">
        {links.map(([l, h]) => (
          <li key={l}>
            <a href={h} className="text-sm text-ink-muted transition-colors hover:text-ink">{l}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
