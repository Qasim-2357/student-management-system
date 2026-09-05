import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const NOTICE_ITEMS = [
  {
    category: "Examinations",
    date: "Current Session",
    title: "End Term Theory & Practical Examination Notification and Schedule",
    href: "/examinations",
    badgeColor: "border-[#D96B27] text-[#D96B27] bg-[#FFF8E7]",
  },
  {
    category: "Academics",
    date: "Current Session",
    title: "Revised Academic Calendar & Semester Instructional Guidelines",
    href: "/academics",
    badgeColor: "border-[#B94E27] text-[#B94E27] bg-[#FFF8E7]",
  },
  {
    category: "Curriculum",
    date: "Current Session",
    title: "Approved Course Syllabi and Evaluation Schemes for Active Programs",
    href: "/curriculum",
    badgeColor: "border-[#6B5A4A] text-[#6B5A4A] bg-[#FFF8E7]",
  },
  {
    category: "General",
    date: "Current Session",
    title: "Official Institutional Circulars, Student Advisories, and Deadlines",
    href: "/notices",
    badgeColor: "border-[#D96B27] text-[#D96B27] bg-[#FFF8E7]",
  },
];

const SERVICE_TILES = [
  {
    title: "Student Registry",
    desc: "Enrollment records, semester status, and student profiles.",
    href: "/dashboard",
  },
  {
    title: "Examinations Desk",
    desc: "Examination timetables, evaluation guidelines, and schedules.",
    href: "/examinations",
  },
  {
    title: "Academic Results",
    desc: "Semester grades, consolidated marksheets, and official transcripts.",
    href: "/results",
  },
  {
    title: "Curriculum & Syllabi",
    desc: "Detailed program schemes, course credits, and core requirements.",
    href: "/curriculum",
  },
  {
    title: "Faculty Directory",
    desc: "Department chairs, academic staff rosters, and office contacts.",
    href: "/faculty",
  },
  {
    title: "Institutional Notices",
    desc: "Official administrative advisories, circulars, and announcements.",
    href: "/notices",
  },
];

const ACADEMIC_DIVISIONS = [
  {
    division: "School of Computing & Information Technology",
    programs: "BCA, B.Tech CS, Data Science & Software Systems",
    summary:
      "Core instruction across data structures, algorithmic design, database architecture, and network security systems.",
  },
  {
    division: "Department of Management & Commerce",
    programs: "BBA, Financial Studies & Business Analytics",
    summary:
      "Applied study covering administrative protocols, quantitative methods, fiscal systems, and managerial reporting.",
  },
  {
    division: "Division of Applied Sciences & Humanities",
    programs: "Applied Mathematics, Statistics & Professional Writing",
    summary:
      "Foundational theoretical coursework emphasizing discrete structures, operational mathematics, and scientific ethics.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* 1. HERO + CAMPUS ARCHITECTURE + NOTICE BOARD */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5]">
          <div className="mx-auto max-w-7xl px-4 py-8 sm:py-10">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-stretch">
              {/* Left Col (7 cols): Campus Hero Plate & Overview */}
              <div
                className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFF8E7] p-5 sm:p-7 lg:col-span-7"
                style={{ borderRadius: "4px" }}
              >
                <div>
                  <div
                    className="mb-3 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFFDF5] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]"
                    style={{ borderRadius: "2px" }}
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
                    Institutional Academic Portal
                  </div>
                  <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
                    Centrally coordinated academic records, examinations, and institutional governance.
                  </h1>
                  <p className="mt-3 text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
                    Student Sphere provides structured administration across curricular frameworks, examination evaluations, and student records for active campus departments.
                  </p>
                </div>

                {/* Grounded Campus Architectural Graphic Plate (CSS & SVG Only) */}
                <div
                  className="relative mt-6 overflow-hidden border border-[#E8D8BD] bg-[#F7EEDC]"
                  style={{ borderRadius: "3px" }}
                >
                  <div className="relative flex aspect-[16/9] w-full flex-col items-center justify-center p-6 text-center">
                    {/* Architectural Grid Linework */}
                    <svg
                      viewBox="0 0 400 200"
                      className="h-28 w-auto text-[#D96B27]"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      {/* Central Dome & Spire */}
                      <path d="M200 20v14" />
                      <path d="M185 45c0-15 15-20 15-20s15 5 15 20h-30z" />
                      <rect x="180" y="45" width="40" height="12" />

                      {/* Pediment / Triangular Gable */}
                      <path d="M120 75L200 45l80 30H120z" />
                      <rect x="110" y="75" width="180" height="10" />

                      {/* Main Portico Columns */}
                      <line x1="130" y1="85" x2="130" y2="155" />
                      <line x1="155" y1="85" x2="155" y2="155" />
                      <line x1="180" y1="85" x2="180" y2="155" />
                      <line x1="220" y1="85" x2="220" y2="155" />
                      <line x1="245" y1="85" x2="245" y2="155" />
                      <line x1="270" y1="85" x2="270" y2="155" />

                      {/* Archway Center Portal */}
                      <path d="M190 155v-30c0-6 4-10 10-10s10 4 10 10v30" />

                      {/* Side Wings / Academics Blocks */}
                      <rect x="40" y="95" width="70" height="60" />
                      <line x1="40" y1="95" x2="110" y2="95" />
                      <rect x="55" y="110" width="16" height="22" />
                      <rect x="80" y="110" width="16" height="22" />

                      <rect x="290" y="95" width="70" height="60" />
                      <line x1="290" y1="95" x2="360" y2="95" />
                      <rect x="305" y="110" width="16" height="22" />
                      <rect x="330" y="110" width="16" height="22" />

                      {/* Plinth / Ground Terrace Steps */}
                      <line x1="20" y1="155" x2="380" y2="155" />
                      <line x1="10" y1="163" x2="390" y2="163" />
                      <line x1="0" y1="171" x2="400" y2="171" />
                    </svg>

                    <span className="mt-3 text-xs font-bold uppercase tracking-wider text-[#3B2921]">
                      Academic Campus &amp; Administrative Quadrangle
                    </span>
                    <span className="mt-0.5 text-[11px] font-medium text-[#6B5A4A]">
                      Central Faculty Registry &amp; Student Learning Complex
                    </span>

                    {/* Bottom Grounding Strip */}
                    <div className="absolute bottom-0 left-0 right-0 border-t border-[#E8D8BD] bg-[#FFFDF5]/95 px-3 py-1.5 text-left text-[11px] font-medium text-[#6B5A4A]">
                      Institutional Administrative Headquarters
                    </div>
                  </div>
                </div>

                {/* Navigation Actions */}
                <div className="mt-6 flex flex-wrap items-center gap-3">
                  <Link
                    href="/login"
                    className="inline-flex items-center border border-[#B94E27] bg-[#D96B27] px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-white transition hover:bg-[#B94E27]"
                    style={{ borderRadius: "3px" }}
                  >
                    Portal Sign In &rarr;
                  </Link>
                  <Link
                    href="/academics"
                    className="inline-flex items-center border border-[#E8D8BD] bg-[#FFFDF5] px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-[#3B2921] transition hover:border-[#D96B27] hover:text-[#D96B27]"
                    style={{ borderRadius: "3px" }}
                  >
                    Explore Academics
                  </Link>
                </div>
              </div>

              {/* Right Col (5 cols): Institutional Notice & Circular Board */}
              <div
                className="flex flex-col border border-[#E8D8BD] bg-[#FFF8E7] p-5 sm:p-6 lg:col-span-5"
                style={{ borderRadius: "4px" }}
              >
                <div className="flex items-center justify-between border-b border-[#E8D8BD] pb-3">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#D96B27]" />
                    <h2 className="font-serif text-sm font-bold uppercase tracking-wider text-[#3B2921]">
                      Notice &amp; Circular Board
                    </h2>
                  </div>
                  <Link
                    href="/notices"
                    className="text-xs font-semibold text-[#D96B27] hover:underline"
                  >
                    View All &rarr;
                  </Link>
                </div>

                <p className="mt-2 text-xs text-[#6B5A4A]">
                  Published announcements and administrative circulars for active student cohorts.
                </p>

                <div className="mt-4 flex flex-1 flex-col divide-y divide-[#E8D8BD]">
                  {NOTICE_ITEMS.map((item, idx) => (
                    <Link
                      key={idx}
                      href={item.href}
                      className="group flex flex-col py-3.5 transition first:pt-1 last:pb-1"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={`inline-block border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${item.badgeColor}`}
                          style={{ borderRadius: "2px" }}
                        >
                          {item.category}
                        </span>
                        <span className="text-[11px] font-medium text-[#6B5A4A]">
                          {item.date}
                        </span>
                      </div>
                      <span className="mt-1.5 text-xs font-semibold text-[#3B2921] group-hover:text-[#D96B27] group-hover:underline">
                        {item.title}
                      </span>
                    </Link>
                  ))}
                </div>

                <div className="mt-4 border-t border-[#E8D8BD] pt-3">
                  <div
                    className="border border-[#E8D8BD] bg-[#FFFDF5] p-3 text-xs text-[#6B5A4A]"
                    style={{ borderRadius: "3px" }}
                  >
                    <span className="font-semibold text-[#3B2921]">Notice Verification:</span> Students must reference official departmental circulars for final hall ticket releases and submission dates.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 2. CORE ACADEMIC SERVICES TILES */}
        <section className="border-b border-[#E8D8BD] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col items-start justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Administrative Desks
                </span>
                <h2 className="font-serif text-xl font-bold tracking-tight text-[#3B2921] sm:text-2xl">
                  Academic &amp; Student Services
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">
                Direct access into institutional operations and student modules.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {SERVICE_TILES.map((service, idx) => (
                <Link
                  key={idx}
                  href={service.href}
                  className="group flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-4 transition hover:border-[#D96B27]"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="font-serif text-sm font-bold text-[#3B2921] group-hover:text-[#D96B27]">
                        {service.title}
                      </span>
                      <span className="text-xs text-[#6B5A4A] group-hover:text-[#D96B27]">
                        &rarr;
                      </span>
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                      {service.desc}
                    </p>
                  </div>
                  <div className="mt-4 border-t border-[#E8D8BD] pt-2 text-[11px] font-medium text-[#D96B27]">
                    Access Division Desk
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* 3. ACADEMIC DIVISIONS & DEPARTMENTS */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Curricular Structure
              </span>
              <h2 className="font-serif text-xl font-bold tracking-tight text-[#3B2921] sm:text-2xl">
                Academic Divisions &amp; Degree Programs
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Institutional departments responsible for accredited coursework, examinations, and faculty allocation.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
              {ACADEMIC_DIVISIONS.map((item, idx) => (
                <div
                  key={idx}
                  className="flex flex-col border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div className="border-b border-[#E8D8BD] pb-3">
                    <h3 className="font-serif text-sm font-bold text-[#3B2921]">
                      {item.division}
                    </h3>
                    <div className="mt-1 text-xs font-semibold text-[#D96B27]">
                      {item.programs}
                    </div>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-[#6B5A4A]">
                    {item.summary}
                  </p>
                  <div className="mt-4 border-t border-[#E8D8BD] pt-3">
                    <Link
                      href="/curriculum"
                      className="inline-flex text-xs font-semibold text-[#D96B27] hover:underline"
                    >
                      View Curricular Syllabus &rarr;
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}