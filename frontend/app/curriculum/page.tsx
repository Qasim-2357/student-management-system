import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const COURSE_MODULES = [
  {
    code: "BCA-101",
    title: "Discrete Mathematics & Linear Structures",
    semester: "Semester I",
    credits: 4,
    type: "Theory Core",
    syllabus: "Set theory, propositional logic, recurrence relations, graph theory fundamentals, and vector spaces.",
  },
  {
    code: "BCA-102",
    title: "Programming with C & Data Structures",
    semester: "Semester I",
    credits: 4,
    type: "Theory + Practical",
    syllabus: "Control structures, memory pointers, dynamic arrays, linked lists, stacks, queues, and tree traversal algorithms.",
  },
  {
    code: "BCA-201",
    title: "Database Management Systems & SQL",
    semester: "Semester III",
    credits: 4,
    type: "Theory + Practical",
    syllabus: "Relational algebra, ER modeling, normal forms (1NF-BCNF), ACID transactions, indexing, and SQL queries.",
  },
  {
    code: "BCA-202",
    title: "Computer Architecture & Organization",
    semester: "Semester III",
    credits: 4,
    type: "Theory Core",
    syllabus: "Register transfer logic, ALU design, microprogrammed control units, instruction pipelines, and cache memory hierarchies.",
  },
  {
    code: "BCA-301",
    title: "Full-Stack Web Engineering",
    semester: "Semester V",
    credits: 4,
    type: "Applied Project",
    syllabus: "HTTP protocols, REST APIs, asynchronous state synchronization, client-side rendering, and backend session management.",
  },
  {
    code: "BCA-302",
    title: "Operating Systems & Concurrency",
    semester: "Semester V",
    credits: 4,
    type: "Theory Core",
    syllabus: "Process scheduling, thread concurrency, mutex locks, semaphores, deadlock handling, and virtual memory paging.",
  },
];

export default function CurriculumPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Curricular Catalog
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Course Curriculum &amp; Syllabi
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Detailed course outlines, module prerequisites, credit weightages, and laboratory requirements approved by the academic board.
            </p>
          </div>
        </section>

        {/* Modules Table */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Module Outlines
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  Active Instructional Syllabi
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">BCA Curricular Matrix (Session 2026–2027)</p>
            </div>

            <div className="overflow-hidden border border-[#E8D8BD] bg-[#FFFDF5]" style={{ borderRadius: "4px" }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#3B2921]">
                  <thead className="border-b border-[#E8D8BD] bg-[#F5EAD4] font-serif text-[11px] font-bold uppercase tracking-wider text-[#3B2921]">
                    <tr>
                      <th className="px-4 py-3">Subject Code</th>
                      <th className="px-4 py-3">Course Title</th>
                      <th className="px-4 py-3">Term</th>
                      <th className="px-4 py-3">Credits &amp; Type</th>
                      <th className="px-4 py-3">Prescribed Syllabus Coverage</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E8D8BD]">
                    {COURSE_MODULES.map((mod) => (
                      <tr key={mod.code} className="hover:bg-[#FFF8E7]/60">
                        <td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-[#D96B27]">
                          {mod.code}
                        </td>
                        <td className="px-4 py-3 font-semibold text-[#3B2921]">
                          {mod.title}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                          {mod.semester}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                          <span className="font-medium text-[#3B2921]">{mod.credits} Credits</span> ({mod.type})
                        </td>
                        <td className="px-4 py-3 text-[#6B5A4A]">
                          {mod.syllabus}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Questions on course registration or exam weightage?</span>
                <p className="text-xs text-[#6B5A4A]">Review the examination guidelines or contact the academic dean.</p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/examinations"
                  className="border border-[#E8D8BD] bg-[#FFF8E7] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27] hover:text-[#D96B27]"
                  style={{ borderRadius: "3px" }}
                >
                  Examinations
                </Link>
                <Link
                  href="/contact"
                  className="border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                  style={{ borderRadius: "3px" }}
                >
                  Contact Desk
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