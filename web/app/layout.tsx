import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { LeadModal } from "@/components/LeadModal";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL("https://verispectai.com"),
  title: "Verispect — Prove your AI behaves, before anyone asks",
  description:
    "Automated EU AI Act compliance monitoring for high-risk AI in hiring, credit, insurance & legal. Active bias & drift detection plus audit-ready evidence — in one line of code. We never see your data.",
  openGraph: {
    title: "Verispect — Automated EU AI Act compliance monitoring",
    description:
      "Active bias & drift detection + audit-ready evidence for high-risk AI. We never see your data. Free AI Act Snapshot in 5 minutes.",
    type: "website",
  },
  icons: { icon: "/logo-mark.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>
        {children}
        <LeadModal />
      </body>
    </html>
  );
}
