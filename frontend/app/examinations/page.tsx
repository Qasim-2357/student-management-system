import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const EXAM_SCHEDULES = [
  {
    code: "BCA-101",
    subject: "Discrete Mathematics & Linear Structures",
    date: "2026-12-24",
    time: "09:30 – 12:30 IST",
    hall: "Examination Hall 1 & 2",
    mode: "Theory Written",
  },
  {
    code: "BCA-102",
    subject: "Programming with C & Data Structures",
    date: "2026-12-27",
    time: "09:30 – 12:30 IST",
    hall: "Examination Hall 1 & 3",
    mode: "Theory Written",
  },
  {
    code: "BCA-103P",
    subject: "Data Structures Practical Demonstration",
    date: "2026-12-30",
    time: "10:00 – 16:00 IST",
    hall: "Computing Lab 2 & 4",
    mode: "Lab Practical + Viva",
  },
  {
    code: "BCA-201",
    subject: "Database Management Systems",
    date: "2027-01-03",
    time: "14:00 – 17:00 IST",
    hall: "Examination Hall 2",
    mode: "Theory Written",
  },
];

const EXAM_RULES = [
  { rule: "Hall Ticket Requirement", detail: "Entry to examination halls requires a signed hall ticket and current institutional student ID card." },
  { rule: "Attendance Eligibility", detail: "A minimum of 75% attendance in theory and laboratory classes is mandatory for term examinations." },
  { rule: "Reporting Timeline", detail: "Students must report 30 minutes prior to the commencement of theory examinations." },
  { rule: "Prohibited Articles", detail: "Mobile devices, programmable calculators, and unauthorized paper materials are strictly prohibited." },
];

export default function ExaminationsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Office of the Controller
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Examinations &amp; Evaluations
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              End-term examination timetables, evaluation regulations, hall ticket notices, and practical assessment schedules.
            </p>
          </div>
        </section>

        {/* Timetable Table */}
        <section className="border-b border-[#E8D8BD] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Timetable
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  End-Term Theory &amp; Practical Schedule
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">Semester I / III / V Regular Examinations</p>
            </div>

            <div className="overflow-hidden border border-[#E8D8BD] bg-[#FFFDF5]" style={{ borderRadius: "4px" }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#3B2921]">
                  <thead className="border-b border-[#E8D8BD] bg-[#F5EAD4] font-serif text-[11px] font-bold uppercase tracking-wider text-[#3B2921]">
                    <tr>
                      <th className="px-4 py-3">Subject Code</th>
                      <th className="px-4 py-3">Course Title</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Reporting Time</th>
                      <th className="px-4 py-3">Hall / Venue</th>
                      <th className="px-4 py-3">Mode</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8D8BD]">
                    {EXAM_SCHEDULES.map((exam) => (
                      <tr key={exam.code} className="hover:bg-[#FFF8E7]/60">
                        <td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-[#D96B27]">
                          {exam.code}
                        </td>
                        <td className="px-4 py-3 font-semibold text-[#3B2921]">
                          {exam.subject}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 font-medium text-[#3B2921]">
                          {exam.date}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                          {exam.time}
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {exam.hall}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 font-medium text-[#D96B27]">
                          {exam.mode}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>

        {/* Regulations Grid */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Regulatory Guidelines
              </span>
              <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                Rules for Examinees
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Standards enforced under institutional examination ordinances.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {EXAM_RULES.map((rule, idx) => (
                <div
                  key={idx}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <h3 className="font-serif text-sm font-bold text-[#3B2921]">
                      {rule.rule}
                    </h3>
                    <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                      {rule.detail}
                    </p>
                  </div>
                  <div className="mt-4 border-t border-[#E8D8BD] pt-2 text-[10px] font-semibold uppercase tracking-wider text-[#6B5A4A]">
                    Examination Ordinance
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Need marksheet verification or semester grade inquiry?</span>
                <p className="text-xs text-[#6B5A4A]">Access student result records or read official circular updates.</p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/results"
                  className="border border-[#E8D8BD] bg-[#FFF8E7] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27] hover:text-[#D96B27]"
                  style={{ borderRadius: "3px" }}
                >
                  Results
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