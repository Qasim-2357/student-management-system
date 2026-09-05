import { PublicHeader } from "@/components/layout/PublicHeader";
import { PublicFooter } from "@/components/layout/PublicFooter";

const CONTACT_DESKS = [
  {
    desk: "Office of the Registrar",
    purpose: "Student admissions, degree matriculation, enrollment verification, and official transcripts.",
    location: "Administrative Block A, Room 101",
    hours: "Monday – Friday: 09:00 – 16:30 IST",
  },
  {
    desk: "Controller of Examinations",
    purpose: "Examination registrations, hall tickets, marksheet corrections, and re-evaluation.",
    location: "Examinations Wing, Room 204",
    hours: "Monday – Friday: 10:00 – 16:00 IST",
  },
  {
    desk: "Academic Deans & Department Registry",
    purpose: "Curriculum counseling, subject allocations, course credit queries, and syllabus outlines.",
    location: "Department of Computing, Room 301",
    hours: "Monday – Friday: 11:00 – 15:30 IST",
  },
  {
    desk: "Student Support & Portal Desk",
    purpose: "Portal account recovery, login credentials, technical troubleshooting, and system support.",
    location: "Central Library Complex, IT Cell",
    hours: "Monday – Saturday: 08:30 – 17:30 IST",
  },
];

export default function ContactPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#FFF8E7] text-[#3B2921]">
      <PublicHeader />

      <main className="flex-1">
        {/* Banner */}
        <section className="border-b border-[#E8D8BD] bg-[#FFFDF5] py-8 sm:py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-2 inline-flex items-center gap-2 border border-[#E8D8BD] bg-[#FFF8E7] px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-[#D96B27]" style={{ borderRadius: "2px" }}>
              <span className="h-1.5 w-1.5 rounded-full bg-[#D96B27]" />
              Institutional Helpdesk
            </div>
            <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921] sm:text-3xl lg:text-4xl">
              Directory &amp; Administrative Desks
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-[#6B5A4A] sm:text-base">
              Office locations, consultation hours, departmental contacts, and portal technical support.
            </p>
          </div>
        </section>

        {/* Contact Desks Grid */}
        <section className="py-10">
          <div className="mx-auto max-w-7xl px-4">
            <div className="mb-6 border-b border-[#E8D8BD] pb-4">
              <span className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">
                Campus Contacts
              </span>
              <h2 className="font-serif text-xl font-bold text-[#3B2921] sm:text-2xl">
                Administrative Office Directory
              </h2>
              <p className="mt-1 text-xs text-[#6B5A4A]">
                Key institutional offices responsible for student records and governance.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              {CONTACT_DESKS.map((desk, idx) => (
                <div
                  key={idx}
                  className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5"
                  style={{ borderRadius: "3px" }}
                >
                  <div>
                    <div className="border-b border-[#E8D8BD] pb-2.5">
                      <h3 className="font-serif text-base font-bold text-[#3B2921]">
                        {desk.desk}
                      </h3>
                    </div>
                    <p className="mt-2.5 text-xs leading-relaxed text-[#6B5A4A]">
                      {desk.purpose}
                    </p>
                    <div className="mt-4 space-y-1 text-xs text-[#6B5A4A]">
                      <p><strong className="text-[#3B2921]">Office Location:</strong> {desk.location}</p>
                      <p><strong className="text-[#3B2921]">Consultation Hours:</strong> {desk.hours}</p>
                    </div>
                  </div>

                  <div className="mt-4 border-t border-[#E8D8BD] pt-2.5 text-[11px] font-medium text-[#D96B27]">
                    Institutional Administrative Desk
                  </div>
                </div>
              ))}
            </div>

            {/* Campus Address & Registry Box */}
            <div className="mt-8 border border-[#E8D8BD] bg-[#FFFDF5] p-5" style={{ borderRadius: "4px" }}>
              <h3 className="font-serif text-base font-bold text-[#3B2921]">
                Institutional Headquarters &amp; Physical Address
              </h3>
              <p className="mt-2 text-xs leading-relaxed text-[#6B5A4A]">
                Student Sphere Central Registry • Campus Administrative Block • Academic Complex<br />
                General Inquiries: Mon – Fri (09:00 – 17:00 IST) • Official Registrar Dispatches
              </p>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}