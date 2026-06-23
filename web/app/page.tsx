import { Navbar } from "@/components/Navbar";
import { Grain, ScrollBeam } from "@/components/fx";
import { Hero } from "@/components/Hero";
import { Struggle } from "@/components/Struggle";
import { Transformation } from "@/components/Transformation";
import { CaseStudy } from "@/components/CaseStudy";
import { Pricing } from "@/components/Pricing";
import { FinalCTA } from "@/components/FinalCTA";
import { Footer } from "@/components/Footer";

export default function Page() {
  return (
    <>
      <Grain />
      <ScrollBeam />
      <Navbar />
      <main>
        <Hero />          {/* Dream Outcome */}
        <Struggle />      {/* Current Struggle */}
        <Transformation />{/* Transformation */}
        <CaseStudy />     {/* Case Study */}
        <Pricing />       {/* Offer */}
        <FinalCTA />      {/* CTA */}
      </main>
      <Footer />
    </>
  );
}
