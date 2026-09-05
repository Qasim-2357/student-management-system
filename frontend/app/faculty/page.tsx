import Link from "next/link";
import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const FACULTY_MEMBERS = [
  {
    name: "Dr. Arvind Ramanathan",
    designation: "Professor & Head of Department",
    department: "Computer Applications",
    qualification: "Ph.D. in Computer Science (Distributed Systems)",
    specialization: "Database Concurrency, High-Performance Systems, Algorithmic Analysis",
    room: "Room 304, Academic Block A",
  },
  {
    name: "Prof. Sunita Deshmukh",
    designation: "Associate Professor",
    department: "Computer Applications",
    qualification: "M.Tech in Software Engineering, M.Phil",
    specialization: "Object-Oriented Design, Web Protocols, Operating System Kernels",
    room: "Room 308, Academic Block A",
  },
  {
    name: "Dr. K. S. Venkatesh",
    designation: "Associate Professor",
    department: "Applied Sciences & Mathematics",
    qualification: "Ph.D. in Applied Mathematics",
    specialization: "Discrete Probability, Graph Theoretical Modeling, Operations Research",
    room: "Room 201, Science Block",
  },
  {
    name: "Prof. Rajesh Mehra",
    designation: "Assistant Professor",
    department: "Computer Applications",
    qualification: "M.Sc. Computer Science, UGC-NET",
    specialization: "Computer Networks, Cryptographic Protocols, Information Security",
    room: "Room 312, Academic Block A",
  },
  {
    name: "Prof. Priya Nair",
    designation: "Assistant Professor",
    department: "Management Studies",
    qualification: "MBA, M.Com (Finance)",
    specialization: "Managerial Accounting, Organizational Economics, Quantitative Analysis",
    room: "Room 105, Management Wing",
  },
  {
    name: "Dr. Manisha Sharma",
    designation: "Assistant Professor",
    department: "Computer Applications",
    qualification: "Ph.D. in Information Systems",
    specialization: "Database Design, Machine Learning Systems, Data Mining",
    room: "Room 315, Academic Block A",
  },
];

export default function FacultyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Academic Roster
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Faculty Directory
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Roster of academic chairs, professors, and teaching fellows guiding instructional delivery and student mentoring.
            </p>
          </div>
        </section>

        {/* Faculty Grid */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 flex flex-col justify-between gap-2 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-end">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                  Instructional Faculty
                </span>
                <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                  Departmental Academic Staff
                </h2>
              </div>
              <p className="text-xs text-[#6B5A4A]">Session 2026–2027 Registered Staff</p>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {FACULTY_MEMBERS.map((faculty, idx) => (
                <div
                  key={idx}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <div className="border-b border-[#E8D8BD] pb-3">
                      <h3 className="font-serif text-base font-bold text-[#3B2921]">
                        {faculty.name}
                      </h3>
                      <div className="text-xs font-semibold text-[#D96B27]">
                        {faculty.designation}
                      </div>
                      <div className="text-[11px] text-[#6B5A4A]">
                        {faculty.department}
                      </div>
                    </div>

                    <div className="mt-3 space-y-1.5 text-xs text-[#6B5A4A]">
                      <p><span className="font-semibold text-[#3B2921]">Credentials:</span> {faculty.qualification}</p>
                      <p><span className="font-semibold text-[#3B2921]">Research / Field:</span> {faculty.specialization}</p>
                      <p><span className="font-semibold text-[#3B2921]">Office:</span> {faculty.room}</p>
                    </div>
                  </div>

                  <div className="mt-4 border-t border-[#E8D8BD] pt-3 text-[11px] font-medium text-[#6B5A4A]">
                    Office Consultation Hours: Mon – Fri (14:00 – 16:00)
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:p-5" style={{ borderRadius: "4px" }}>
              <div>
                <span className="text-xs font-bold text-[#3B2921]">Need institutional assistance or administrative contact?</span>
                <p className="text-xs text-[#6B5A4A]">Reach the Dean of Academics or the Registrar&apos;s support desk.</p>
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