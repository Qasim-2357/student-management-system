import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const CORE_PILLARS = [
  {
    code: "ADM-01",
    title: "Centrally Coordinated Governance",
    desc: "Single-source administrative management for student matriculation, curricular cataloging, and faculty allocations across all active academic divisions.",
  },
  {
    code: "EVAL-02",
    title: "Evaluation & Transcript Integrity",
    desc: "Standardized grading frameworks, continuous internal evaluations, and tamper-resistant semester result reporting aligned with accredited university guidelines.",
  },
  {
    code: "REG-03",
    title: "Instructional Continuity & Compliance",
    desc: "Direct tracking of curriculum delivery, session timetables, attendance minimums, and regulatory notices required for accredited degree progression.",
  },
  {
    code: "SEC-04",
    title: "Confidentiality & Role-Gated Access",
    desc: "Strict administrative authorization safeguarding student demographic files, fee ledger entries, and performance records under departmental access controls.",
  },
];

const INSTITUTIONAL_MILESTONES = [
  {
    year: "Charter Phase",
    heading: "Institutional System Inception",
    detail: "Consolidation of fragmented departmental registers into a unified digital schema covering student admissions, subject codes, and course credits.",
  },
  {
    year: "Curricular Phase",
    heading: "Syllabus & Faculty Standardization",
    detail: "Deployment of standardized syllabus matrices and faculty assignment modules to oversee course progress and student attendance compliance.",
  },
  {
    year: "Evaluation Phase",
    heading: "Integrated Examination Office",
    detail: "Automation of semester marksheet compilation, GPA calculations, and official notice dispatches through the centralized registry portal.",
  },
];

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Header Title Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Institutional Overview
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              About Student Sphere
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              The official administrative and academic operations portal. Built to coordinate student lifecycles, institutional regulations, curricular delivery, and transparent examination evaluations.
            </p>
          </div>
        </section>

        {/* Institutional Purpose & Charter (Split Section) */}
        <section className="border-b border-[#E8D8BD] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-stretch">
              {/* Institutional Purpose */}
              <div
                className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-6 sm:p-8 lg:col-span-7"
                style={{ borderRadius: "4px" }}
              >
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                    Institutional Charter
                  </span>
                  <h2 className="mt-1 font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                    Administrative Mission &amp; Purpose
                  </h2>
                  <div className="mt-4 space-y-3 text-xs leading-relaxed text-[#6B5A4A] sm:text-sm">
                    <p>
                      Student Sphere operates as the authoritative platform connecting students, faculty members, and academic administrators. By digitizing institutional workflows, the platform enforces compliance with university ordinances, session calendars, and standardized evaluation benchmarks.
                    </p>
                    <p>
                      The system replaces siloed paperwork with secure, verifiable digital records—ensuring that attendance registers, fee compliance, internal assessments, and end-term results are reconciled under verified oversight.
                    </p>
                  </div>
                </div>

                <div className="mt-6 border-t border-[#E8D8BD] pt-4">
                  <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-[#6B5A4A]">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-[#D96B27]" />
                      Session 2026–2027 Framework
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-[#E8A317]" />
                      Accredited Governance Schema
                    </span>
                  </div>
                </div>
              </div>

              {/* Departmental Structure Panel */}
              <div
                className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-6 sm:p-8 lg:col-span-5"
                style={{ borderRadius: "4px" }}
              >
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                    Oversight Hierarchy
                  </span>
                  <h2 className="mt-1 font-serif text-lg font-bold text-[#3B2921] sm:text-xl">
                    Academic Governance Desks
                  </h2>

                  <div className="mt-4 divide-y divide-[#E8D8BD]">
                    <div className="py-2.5 first:pt-0">
                      <span className="text-xs font-bold text-[#3B2921]">Office of the Registrar</span>
                      <p className="mt-0.5 text-xs text-[#6B5A4A]">Student matriculation records, enrollment rolls, and formal institutional documentation.</p>
                    </div>
                    <div className="py-2.5">
                      <span className="text-xs font-bold text-[#3B2921]">Controller of Examinations</span>
                      <p className="mt-0.5 text-xs text-[#6B5A4A]">Examination timetables, marksheet generation, grade moderation, and tabulation registers.</p>
                    </div>
                    <div className="py-2.5 last:pb-0">
                      <span className="text-xs font-bold text-[#3B2921]">Academic Deans &amp; Faculty Chairs</span>
                      <p className="mt-0.5 text-xs text-[#6B5A4A]">Curriculum planning, syllabus tracking, attendance reconciliation, and classroom allocations.</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 border-t border-[#E8D8BD] pt-4">
                  <Link
                    href="/contact"
                    className="inline-flex text-xs font-semibold text-[#D96B27] hover:underline"
                  >
                    View Administrative Directory &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Operational Pillars Grid */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                System Architecture
              </span>
              <h2 className="font-serif text-xl font-bold tracking-tight text-[#3B2921] sm:text-2xl">
                Core Operational Pillars
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Foundational standards governing student records and campus administration.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {CORE_PILLARS.map((pillar) => (
                <div
                  key={pillar.code}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFF8E7] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <span className="inline-block border border-[#E8D8BD] bg-[#FFFDF5] px-2 py-0.5 text-[10px] font-bold text-[#D96B27]" style={{ borderRadius: "2px" }}>
                      {pillar.code}
                    </span>
                    <h3 className="mt-3 font-serif text-sm font-bold text-[#3B2921]">
                      {pillar.title}
                    </h3>
                    <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                      {pillar.desc}
                    </p>
                  </div>
                  <div className="mt-4 border-t border-[#E8D8BD] pt-2 text-[10px] font-semibold uppercase tracking-wider text-[#6B5A4A]">
                    Standard Protocol
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* System Evolution / Milestones */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Development Roadmap
              </span>
              <h2 className="font-serif text-xl font-bold tracking-tight text-[#3B2921] sm:text-2xl">
                Evolution of Student Sphere
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Phased implementation of central academic and examination management tools.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              {INSTITUTIONAL_MILESTONES.map((item, idx) => (
                <div
                  key={idx}
                  className="border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <span className="text-xs font-bold text-[#D96B27]">
                    {item.year}
                  </span>
                  <h3 className="mt-1 font-serif text-sm font-bold text-[#3B2921]">
                    {item.heading}
                  </h3>
                  <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                    {item.detail}
                  </p>
                </div>
              ))}
            </div>

            {/* Practical Navigation Strip */}
            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Looking to review curriculum schemes or exam circulars?</span>
                <p className="text-xs text-[#6B5A4A]">Explore current instructional syllabi or check active circular releases.</p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/curriculum"
                  className="border border-[#E8D8BD] bg-[#FFF8E7] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27] hover:text-[#D96B27]"
                  style={{ borderRadius: "3px" }}
                >
                  Curriculum
                </Link>
                <Link
                  href="/notices"
                  className="border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                  style={{ borderRadius: "3px" }}
                >
                  Notices
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}