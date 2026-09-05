"use client";

import { useRouter } from "next/navigation";
import { StudentForm } from "@/components/students/StudentForm";
import { useCreateStudent } from "@/lib/hooks/use-students";
import type { StudentCreate } from "@/lib/types/students";
import Link from "next/link";

export default function NewStudentPage() {
  const router = useRouter();
  const createMutation = useCreateStudent();

  const handleSubmit = async (data: StudentCreate) => {
    try {
      const created = await createMutation.mutateAsync(data);
      const newId = (created as unknown as { id?: number })?.id;
      if (newId) {
        router.push(`/students/${newId}`);
      } else {
        router.push("/students");
      }
    } catch {
      alert("Failed to register student. Please verify all required fields and unique credentials.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Title Header */}
      <div className="flex items-center justify-between border-b border-[#E8D8BD] pb-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">Admission Registry</div>
          <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921]">
            Register New Student
          </h1>
          <p className="mt-0.5 text-xs text-[#6B5A4A]">
            Enter demographic, matriculation, and academic class allocation details.
          </p>
        </div>

        <Link
          href="/students"
          className="border border-[#E8D8BD] bg-[#FFFDF5] px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27]"
          style={{ borderRadius: "3px" }}
        >
          ← Return to Directory
        </Link>
      </div>

      {/* Form Container */}
      <div className="border border-[#E8D8BD] bg-[#FFFDF5] p-6" style={{ borderRadius: "4px" }}>
        <StudentForm
          onSubmit={handleSubmit}
          busy={createMutation.isPending}
          submitLabel={createMutation.isPending ? "Submitting Registration..." : "Complete Matriculation"}
        />
      </div>
    </div>
  );
}