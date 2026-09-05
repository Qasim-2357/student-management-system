"use client";

import { use } from "react";
import Link from "next/link";
import { useStudent } from "@/lib/hooks/use-students";
import { useClasses } from "@/lib/hooks/use-classes";
import { LoadingState } from "@/components/states/LoadingState";
import { ErrorState } from "@/components/states/ErrorState";
import { RoleGate } from "@/components/role/RoleGate";

export default function StudentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const studentId = Number(resolvedParams.id);

  const { data: studentResponse, isLoading, isError, error, refetch } = useStudent(studentId);
  const { data: classesResponse } = useClasses({});

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError || !studentResponse) {
    return (
      <ErrorState
        title="Student Not Found"
        message={error instanceof Error ? error.message : "The requested student record could not be loaded."}
        onRetry={() => refetch()}
      />
    );
  }

  const studentObj = studentResponse as unknown as Record<string, unknown>;

  const classList = (() => {
    if (!classesResponse) return [];
    if (Array.isArray(classesResponse)) return classesResponse;
    const res = classesResponse as unknown as { items?: Array<{ id: number; name: string; academic_year?: string }>; data?: Array<{ id: number; name: string; academic_year?: string }> };
    return res.items ?? res.data ?? [];
  })();

  const assignedClass = classList.find((c) => c.id === studentResponse.academic_class_id);

  const studentName =
    typeof studentObj.name === "string" && studentObj.name
      ? studentObj.name
      : `${studentObj.first_name ?? ""} ${studentObj.last_name ?? ""}`.trim() || `Student #${studentId}`;

  const rollNumber = typeof studentResponse.roll_number === "string" ? studentResponse.roll_number : "—";
  const email = typeof studentResponse.email === "string" ? studentResponse.email : "—";
  const phone = typeof studentObj.phone_number === "string" ? studentObj.phone_number : "None Recorded";
  const enrollmentDate = typeof studentObj.enrollment_date === "string" ? studentObj.enrollment_date : "—";
  const isActive = (studentObj.is_active as boolean | undefined) ?? true;

  return (
    <div className="space-y-6">
      {/* Top Header / Actions */}
      <div className="flex flex-col gap-3 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">Student Dossier</div>
          <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921]">
            {studentName}
          </h1>
          <p className="mt-0.5 font-mono text-xs text-[#6B5A4A]">Roll Number: {rollNumber}</p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/students"
            className="border border-[#E8D8BD] bg-[#FFFDF5] px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-[#3B2921] hover:border-[#D96B27]"
            style={{ borderRadius: "3px" }}
          >
            ← Back to Directory
          </Link>

          <RoleGate roles={["admin"]}>
            <Link
              href={`/students/${studentId}/edit`}
              className="border border-[#B94E27] bg-[#D96B27] px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
              style={{ borderRadius: "3px" }}
            >
              Edit Details
            </Link>
          </RoleGate>
        </div>
      </div>

      {/* Grid: Demographics + Academic Class Allocation */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Demographics */}
        <div className="border border-[#E8D8BD] bg-[#FFFDF5] p-5 lg:col-span-2" style={{ borderRadius: "4px" }}>
          <h2 className="border-b border-[#E8D8BD] pb-2.5 font-serif text-sm font-bold text-[#3B2921]">
            Demographic &amp; Institutional Profile
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 text-xs">
            <div>
              <span className="font-bold text-[#6B5A4A]">Full Legal Name:</span>
              <p className="mt-0.5 font-semibold text-[#3B2921]">{studentName}</p>
            </div>
            <div>
              <span className="font-bold text-[#6B5A4A]">Institutional Roll Number:</span>
              <p className="mt-0.5 font-mono font-bold text-[#D96B27]">{rollNumber}</p>
            </div>
            <div>
              <span className="font-bold text-[#6B5A4A]">Email Address:</span>
              <p className="mt-0.5 text-[#3B2921]">{email}</p>
            </div>
            <div>
              <span className="font-bold text-[#6B5A4A]">Contact Phone:</span>
              <p className="mt-0.5 text-[#3B2921]">{phone}</p>
            </div>
            <div>
              <span className="font-bold text-[#6B5A4A]">Matriculation Date:</span>
              <p className="mt-0.5 text-[#3B2921]">{enrollmentDate}</p>
            </div>
            <div>
              <span className="font-bold text-[#6B5A4A]">Registration Status:</span>
              <p className="mt-0.5">
                <span
                  className={`inline-block border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                    isActive
                      ? "border-[#E8D8BD] bg-[#FFF8E7] text-[#D96B27]"
                      : "border-[#E8D8BD] bg-[#F3EFE6] text-[#6B5A4A]"
                  }`}
                  style={{ borderRadius: "2px" }}
                >
                  {isActive ? "Active" : "Inactive"}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Class & Cohort */}
        <div className="flex flex-col justify-between border border-[#E8D8BD] bg-[#FFFDF5] p-5" style={{ borderRadius: "4px" }}>
          <div>
            <h2 className="border-b border-[#E8D8BD] pb-2.5 font-serif text-sm font-bold text-[#3B2921]">
              Academic Allocation
            </h2>
            {assignedClass ? (
              <div className="mt-4 space-y-2 text-xs">
                <div>
                  <span className="font-bold text-[#6B5A4A]">Cohort Name:</span>
                  <p className="mt-0.5 font-semibold text-[#3B2921]">{assignedClass.name}</p>
                </div>
                <div>
                  <span className="font-bold text-[#6B5A4A]">Academic Session:</span>
                  <p className="mt-0.5 text-[#3B2921]">{assignedClass.academic_year ?? "Current Session"}</p>
                </div>
              </div>
            ) : (
              <p className="mt-4 text-xs italic text-[#6B5A4A]">Student is currently unassigned to an academic class.</p>
            )}
          </div>

          <div className="mt-6 border-t border-[#E8D8BD] pt-3 text-[11px] text-[#6B5A4A]">
            Enrolled in Central Registry
          </div>
        </div>
      </div>
    </div>
  );
}