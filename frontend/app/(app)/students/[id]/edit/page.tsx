"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useStudent, useUpdateStudent } from "@/lib/hooks/use-students";
import { StudentForm } from "@/components/students/StudentForm";
import { LoadingState } from "@/components/states/LoadingState";
import { ErrorState } from "@/components/states/ErrorState";
import type { StudentUpdate } from "@/lib/types/students";

export default function EditStudentPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const studentId = Number(resolvedParams.id);
  const router = useRouter();

  const { data: student, isLoading, isError, error, refetch } = useStudent(studentId);
  const updateMutation = useUpdateStudent(studentId);

  const handleSubmit = async (data: StudentUpdate) => {
    try {
      await updateMutation.mutateAsync(data);
      router.push(`/students/${studentId}`);
    } catch {
      alert("Failed to update student profile. Please verify data format.");
    }
  };

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError || !student) {
    return (
      <ErrorState
        title="Student Not Found"
        message={error instanceof Error ? error.message : "The requested student could not be located."}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between border-b border-[#E8D8BD] pb-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">Profile Modification</div>
          <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921]">
            Edit Student #{student.id}
          </h1>
          <p className="mt-0.5 font-mono text-xs text-[#6B5A4A]">Roll Number: {student.roll_number}</p>
        </div>

        <Link
          href={`/students/${student.id}`}
          className="border border-[#E8D8BD] bg-[#FFFDF5] px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27]"
          style={{ borderRadius: "3px" }}
        >
          Cancel
        </Link>
      </div>

      <div className="border border-[#E8D8BD] bg-[#FFFDF5] p-6" style={{ borderRadius: "4px" }}>
        <StudentForm
          initialData={student}
          onSubmit={handleSubmit}
          busy={updateMutation.isPending}
          submitLabel={updateMutation.isPending ? "Updating..." : "Update Student Record"}
        />
      </div>
    </div>
  );
}