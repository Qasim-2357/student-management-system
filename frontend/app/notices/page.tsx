import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const OFFICIAL_NOTICES = [
  {
    id: "CIR-2026-088",
    category: "Examinations",
    date: "Current Academic Session",
    title: "Final Schedule for End-Term Theory & Practical Examinations",
    issuer: "Office of Controller of Examinations",
    summary: "Timetable schedules for odd semesters uploaded. Students are advised to verify their subject codes and exam session timings on their hall tickets.",
  },
  {
    id: "CIR-2026-082",
    category: "Academics",
    date: "Current Academic Session",
    title: "Instructional Guidelines on Attendance Minimums & Eligibility",
    issuer: "Office of the Academic Dean",
    summary: "Mandatory requirement of 75% attendance for appearing in end-term university evaluations. Shortfall rosters published on student portals.",
  },
  {
    id: "CIR-2026-079",
    category: "Registry",
    date: "Current Academic Session",
    title: "Semester Course Registration & Elective Confirmation Window",
    issuer: "Academic Registry",
    summary: "All enrolled students must confirm their disciplinary and open-elective subjects via the student management portal before the terminal deadline.",
  },
  {
    id: "CIR-2026-074",
    category: "General",
    date: "Current Academic Session",
    title: "Institutional Identity Card Re-issuance Protocols",
    issuer: "Campus Administrative Cell",
    summary: "Instructions for replacement of damaged or lost student smart cards through the central registrar desk.",
  },
];

export default function NoticesPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Official Gazette
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Notices &amp; Circulars
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Administrative dispatches, examination notices, academic circulars, and institutional announcements.
            </p>
          </div>
        </section>

        {/* Notices Board */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Dispatches
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  Active Administrative Circulars
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">Session 2026–2027 Dispatches</p>
            </div>

            <div className="space-y-4">
              {OFFICIAL_NOTICES.map((notice) => (
                <div
                  key={notice.id}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5 transition hover:border-[#D96B27]"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#E8D8BD] pb-2.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-[#D96B27]">
                          {notice.id}
                        </span>
                        <span className="border border-[#E8D8BD] bg-[#FFF8E7] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#3B2921]" style={{ borderRadius: "2px" }}>
                          {notice.category}
                        </span>
                      </div>
                      <span className="text-xs font-medium text-[#6B5A4A]">
                        {notice.date}
                      </span>
                    </div>

                    <h3 className="mt-3 font-serif text-base font-bold text-[#3B2921]">
                      {notice.title}
                    </h3>
                    <p className="mt-1 text-xs leading-relaxed text-[#6B5A4A]">
                      {notice.summary}
                    </p>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-[#E8D8BD] pt-3 text-xs text-[#6B5A4A]">
                    <span>Authority: <strong className="text-[#3B2921]">{notice.issuer}</strong></span>
                    <span className="text-[11px] font-semibold text-[#D96B27]">Formal Gazette Release</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Need formal verification of a circular or notice?</span>
                <p className="text-xs text-[#6B5A4A]">Inquire directly with the Office of the Registrar.</p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/contact"
                  className="border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                  style={{ borderRadius: "3px" }}
                >
                  Contact Registry
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