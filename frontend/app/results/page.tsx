import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const RESULT_ANNOUNCEMENTS = [
  {
    session: "May–June Session",
    term: "BCA Semester IV Regular Examination",
    status: "Published",
    date: "Current Session",
    desc: "Consolidated grade cards and semester marksheets dispatched to departmental offices.",
  },
  {
    session: "May–June Session",
    term: "BCA Semester II Regular Examination",
    status: "Published",
    date: "Current Session",
    desc: "Tabulation registers verified and signed by Controller of Examinations.",
  },
  {
    session: "Special Supplementary",
    term: "Semester I Re-evaluation & Backlog",
    status: "Finalized",
    date: "Current Session",
    desc: "Re-evaluation grade moderation concluded and recorded in central registrar ledger.",
  },
];

const GRADING_SCALE = [
  { grade: "O", points: "10.0", range: "90% – 100%", descriptor: "Outstanding" },
  { grade: "A+", points: "9.0", range: "80% – 89%", descriptor: "Excellent" },
  { grade: "A", points: "8.0", range: "70% – 79%", descriptor: "Very Good" },
  { grade: "B+", points: "7.0", range: "60% – 69%", descriptor: "Good" },
  { grade: "B", points: "6.0", range: "50% – 59%", descriptor: "Above Average" },
  { grade: "C", points: "5.0", range: "40% – 49%", descriptor: "Pass Minimum" },
  { grade: "F", points: "0.0", range: "Below 40%", descriptor: "Fail / Re-appear" },
];

export default function ResultsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Evaluation Office
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Academic Results &amp; Transcripts
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Official semester result declarations, grading scales, transcript verification guidelines, and re-evaluation procedures.
            </p>
          </div>
        </section>

        {/* Result Declarations */}
        <section className="border-b border-[#E8D8BD] py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Published Statements
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  Recent Result Declarations
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">Official Tabulation Dispatches</p>
            </div>

            <div className="space-y-3">
              {RESULT_ANNOUNCEMENTS.map((res, idx) => (
                <div
                  key={idx}
                  className="flex flex-col justify-between gap-3 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:flex-row sm:items-center"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="border border-[#D96B27] bg-[#FFF8E7] px-2 py-0.5 text-[10px] font-bold text-[#D96B27]" style={{ borderRadius: "2px" }}>
                        {res.status}
                      </span>
                      <span className="text-[11px] font-medium text-[#6B5A4A]">
                        {res.session} • {res.date}
                      </span>
                    </div>
                    <h3 className="mt-1 font-serif text-sm font-bold text-[#3B2921]">
                      {res.term}
                    </h3>
                    <p className="text-xs text-[#6B5A4A]">
                      {res.desc}
                    </p>
                  </div>

                  <Link
                    href="/login"
                    className="inline-flex shrink-0 items-center border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                    style={{ borderRadius: "3px" }}
                  >
                    View in Student Portal &rarr;
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Grading Scale */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Standard Framework
              </span>
              <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                10-Point Institutional Grading Scale
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Prescribed credit point mapping for CGPA / SGPA calculation.
              </p>
            </div>

            <div className="overflow-hidden border border-[#E8D8BD] bg-[#FFFDF5]" style={{ borderRadius: "4px" }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#3B2921]">
                  <thead className="border-b border-[#E8D8BD] bg-[#F5EAD4] font-serif text-[11px] font-bold uppercase tracking-wider text-[#3B2921]">
                    <tr>
                      <th className="px-4 py-3">Letter Grade</th>
                      <th className="px-4 py-3">Grade Point</th>
                      <th className="px-4 py-3">Marks Percentage Range</th>
                      <th className="px-4 py-3">Academic Descriptor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8D8BD]">
                    {GRADING_SCALE.map((scale) => (
                      <tr key={scale.grade} className="hover:bg-[#FFF8E7]/60">
                        <td className="px-4 py-3 font-mono font-bold text-[#D96B27]">
                          {scale.grade}
                        </td>
                        <td className="px-4 py-3 font-semibold text-[#3B2921]">
                          {scale.points}
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {scale.range}
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {scale.descriptor}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}