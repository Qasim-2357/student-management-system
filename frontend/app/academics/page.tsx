import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const ACADEMIC_PROGRAMS = [
  {
    code: "UG-BCA-101",
    name: "Bachelor of Computer Applications (BCA)",
    division: "School of Computing & Information Technology",
    duration: "3 Years (6 Semesters)",
    credits: "140 Credits",
    focus: "Data Structures, Database Architecture, Web Engineering, Software System Design.",
  },
  {
    code: "UG-CS-102",
    name: "B.Tech in Computer Science & Engineering",
    division: "School of Computing & Information Technology",
    duration: "4 Years (8 Semesters)",
    credits: "160 Credits",
    focus: "Operating Systems, Computer Networks, Compilers, Algorithmic Analysis.",
  },
  {
    code: "UG-BBA-201",
    name: "Bachelor of Business Administration (BBA)",
    division: "Department of Management & Commerce",
    duration: "3 Years (6 Semesters)",
    credits: "135 Credits",
    focus: "Managerial Economics, Quantitative Methods, Organizational Behavior, Fiscal Analytics.",
  },
  {
    code: "UG-DS-301",
    name: "B.Sc. in Applied Statistics & Data Analytics",
    division: "Division of Applied Sciences & Humanities",
    duration: "3 Years (6 Semesters)",
    credits: "138 Credits",
    focus: "Probability Models, Discrete Mathematics, Statistical Computing, Regression Frameworks.",
  },
];

const CALENDAR_EVENTS = [
  { term: "Semester Term", dates: "August 01 – December 15", desc: "Instructional Teaching Term & Continuous Internal Evaluation (CIE)." },
  { term: "Mid-Term Evaluations", dates: "October 10 – October 18", desc: "Mid-semester internal theory tests and practical demonstrations." },
  { term: "Preparatory Recess", dates: "December 16 – December 22", desc: "Study break and clearance of departmental lab journals." },
  { term: "End-Term University Exams", dates: "December 23 – January 15", desc: "Final theory examinations and external practical assessment." },
];

export default function AcademicsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Academic Registry
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Academic Programs &amp; Regulations
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Accredited degree structures, credit frameworks, academic calendars, and instructional standards coordinated across departments.
            </p>
          </div>
        </section>

        {/* Programs Catalog Table */}
        <section className="border-b border-[#E8D8BD] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Degree Schemes
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  Accredited Program Offerings
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">Session 2026–2027 Registered Curriculum</p>
            </div>

            <div className="overflow-hidden border border-[#E8D8BD] bg-[#FFFDF5]" style={{ borderRadius: "4px" }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#3B2921]">
                  <thead className="border-b border-[#E8D8BD] bg-[#F5EAD4] font-serif text-[11px] font-bold uppercase tracking-wider text-[#3B2921]">
                    <tr>
                      <th className="px-4 py-3">Program Code</th>
                      <th className="px-4 py-3">Degree Name</th>
                      <th className="px-4 py-3">Academic Division</th>
                      <th className="px-4 py-3">Duration &amp; Credits</th>
                      <th className="px-4 py-3">Curricular Focus</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8D8BD]">
                    {ACADEMIC_PROGRAMS.map((prog) => (
                      <tr key={prog.code} className="hover:bg-[#FFF8E7]/60">
                        <td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-[#D96B27]">
                          {prog.code}
                        </td>
                        <td className="px-4 py-3 font-semibold text-[#3B2921]">
                          {prog.name}
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {prog.division}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                          {prog.duration} • <span className="font-medium text-[#3B2921]">{prog.credits}</span>
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {prog.focus}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>

        {/* Academic Calendar Guidelines */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Session Schedule
              </span>
              <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                Annual Academic Calendar
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Key dates governing instructional terms, examinations, and vacation periods.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {CALENDAR_EVENTS.map((event, idx) => (
                <div
                  key={idx}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <span className="text-[11px] font-bold text-[#D96B27]">
                      {event.dates}
                    </span>
                    <h3 className="mt-1 font-serif text-sm font-bold text-[#3B2921]">
                      {event.term}
                    </h3>
                    <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                      {event.desc}
                    </p>
                  </div>
                  <div className="mt-4 border-t border-[#E8D8BD] pt-2 text-[10px] font-semibold uppercase tracking-wider text-[#6B5A4A]">
                    Official Schedule
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Looking for course syllabi or exam guidelines?</span>
                <p className="text-xs text-[#6B5A4A]">Access subject-wise module outlines and examination evaluation criteria.</p>
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
                  href="/examinations"
                  className="border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                  style={{ borderRadius: "3px" }}
                >
                  Examinations
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