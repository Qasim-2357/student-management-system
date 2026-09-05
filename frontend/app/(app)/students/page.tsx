"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useStudents, useDeleteStudent } from "@/lib/hooks/use-students";
import { useClasses } from "@/lib/hooks/use-classes";
import { LoadingState } from "@/components/states/LoadingState";
import { ErrorState } from "@/components/states/ErrorState";
import { EmptyState } from "@/components/states/EmptyState";
import { RoleGate } from "@/components/role/RoleGate";
import type { Student } from "@/lib/types/students";

export default function StudentsPage() {
  const [search, setSearch] = useState("");
  const [selectedClassId, setSelectedClassId] = useState<number | undefined>(undefined);
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const { data: studentsResponse, isLoading, isError, error, refetch } = useStudents({
    page,
    page_size: pageSize,
    academic_class_id: selectedClassId,
  });

  const { data: classesResponse } = useClasses({});
  const deleteMutation = useDeleteStudent();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Safely extract arrays from paginated response structures
  const studentList: Student[] = useMemo(() => {
    if (!studentsResponse) return [];
    if (Array.isArray(studentsResponse)) return studentsResponse;
    const res = studentsResponse as unknown as { items?: Student[]; data?: Student[] };
    return res.items ?? res.data ?? [];
  }, [studentsResponse]);

  const classList = useMemo(() => {
    if (!classesResponse) return [];
    if (Array.isArray(classesResponse)) return classesResponse;
    const res = classesResponse as unknown as { items?: Array<{ id: number; name: string; academic_year?: string }>; data?: Array<{ id: number; name: string; academic_year?: string }> };
    return res.items ?? res.data ?? [];
  }, [classesResponse]);

  const filteredStudents = useMemo(() => {
    if (!search.trim()) return studentList;
    const q = search.toLowerCase();
    return studentList.filter((s: Student) => {
      const studentObj = s as unknown as Record<string, unknown>;
      const displayName =
        typeof studentObj.name === "string"
          ? studentObj.name
          : `${studentObj.first_name ?? ""} ${studentObj.last_name ?? ""}`;
      const roll = typeof s.roll_number === "string" ? s.roll_number : "";
      const email = typeof s.email === "string" ? s.email : "";

      return (
        displayName.toLowerCase().includes(q) ||
        roll.toLowerCase().includes(q) ||
        email.toLowerCase().includes(q)
      );
    });
  }, [studentList, search]);

  const getStudentName = (student: Student): string => {
    const studentObj = student as unknown as Record<string, unknown>;
    if (typeof studentObj.name === "string" && studentObj.name) return studentObj.name;
    const first = typeof studentObj.first_name === "string" ? studentObj.first_name : "";
    const last = typeof studentObj.last_name === "string" ? studentObj.last_name : "";
    return `${first} ${last}`.trim() || `Student #${student.id}`;
  };

  const handleDelete = async (student: Student) => {
    const studentName = getStudentName(student);
    const confirmed = window.confirm(
      `Are you sure you want to remove student "${studentName}" (${student.roll_number})? This action cannot be undone.`
    );
    if (!confirmed) return;

    try {
      setDeletingId(student.id);
      await deleteMutation.mutateAsync(student.id);
    } catch {
      alert("Failed to delete student. Please try again.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Registration Action */}
      <div className="flex flex-col gap-3 border-b border-[#E8D8BD] pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-widest text-[#D96B27]">Student Directory</div>
          <h1 className="font-serif text-2xl font-bold tracking-tight text-[#3B2921]">
            Registered Students
          </h1>
          <p className="mt-0.5 text-xs text-[#6B5A4A]">
            Manage student matriculation, class allotments, and academic profiles.
          </p>
        </div>

        <RoleGate roles={["admin"]}>
          <Link
            href="/students/new"
            className="inline-flex items-center border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white shadow-xs transition hover:bg-[#B94E27]"
            style={{ borderRadius: "3px" }}
          >
            + Register Student
          </Link>
        </RoleGate>
      </div>

      {/* Search & Class Filter Strip */}
      <div className="flex flex-col gap-3 border border-[#E8D8BD] bg-[#FFFDF5] p-4 sm:flex-row sm:items-center sm:justify-between" style={{ borderRadius: "4px" }}>
        <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="text"
            placeholder="Search by name, roll number, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] placeholder-[#6B5A4A] focus:border-[#D96B27] focus:outline-none sm:max-w-md"
            style={{ borderRadius: "3px" }}
          />

          <select
            value={selectedClassId ?? ""}
            onChange={(e) => {
              setSelectedClassId(e.target.value ? Number(e.target.value) : undefined);
              setPage(1);
            }}
            className="border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-2 text-xs text-[#3B2921] focus:border-[#D96B27] focus:outline-none sm:w-56"
            style={{ borderRadius: "3px" }}
          >
            <option value="">All Academic Classes</option>
            {classList.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} {c.academic_year ? `(${c.academic_year})` : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="text-xs font-medium text-[#6B5A4A]">
          Showing {filteredStudents.length} records
        </div>
      </div>

      {/* Data Surface */}
      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState
          title="Could not load students"
          message={error instanceof Error ? error.message : "Database connection error."}
          onRetry={() => refetch()}
        />
      ) : filteredStudents.length === 0 ? (
        <div className="space-y-4">
          <EmptyState
            title="No Students Found"
            description="There are no students matching the specified criteria."
          />
          <div className="flex justify-center">
            <RoleGate roles={["admin"]}>
              <Link
                href="/students/new"
                className="inline-flex items-center border border-[#B94E27] bg-[#D96B27] px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white hover:bg-[#B94E27]"
                style={{ borderRadius: "3px" }}
              >
                Register Student
              </Link>
            </RoleGate>
          </div>
        </div>
      ) : (
        <div className="overflow-hidden border border-[#E8D8BD] bg-[#FFFDF5] shadow-xs" style={{ borderRadius: "4px" }}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#3B2921]">
              <thead className="border-b border-[#E8D8BD] bg-[#F5EAD4] font-serif text-[11px] font-bold uppercase tracking-wider text-[#3B2921]">
                <tr>
                  <th className="px-4 py-3">Roll No.</th>
                  <th className="px-4 py-3">Student Name</th>
                  <th className="px-4 py-3">Email Address</th>
                  <th className="px-4 py-3">Class</th>
                  <th className="px-4 py-3">Enrollment Date</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8D8BD]">
                {filteredStudents.map((student: Student) => {
                  const studentObj = student as unknown as Record<string, unknown>;
                  const assignedClass = classList.find((c) => c.id === student.academic_class_id);
                  const name = getStudentName(student);
                  const enrollmentDate = typeof studentObj.enrollment_date === "string" ? studentObj.enrollment_date : "—";
                  const isActive = (studentObj.is_active as boolean | undefined) ?? true;

                  return (
                    <tr key={student.id} className="hover:bg-[#FFF8E7]/70">
                      <td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-[#D96B27]">
                        <Link href={`/students/${student.id}`} className="hover:underline">
                          {student.roll_number}
                        </Link>
                      </td>
                      <td className="px-4 py-3 font-semibold text-[#3B2921]">
                        <Link href={`/students/${student.id}`} className="hover:underline">
                          {name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-[#6B5A4A]">{student.email}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                        {assignedClass ? assignedClass.name : "Unassigned"}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-[#6B5A4A]">
                        {enrollmentDate}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3">
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
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            href={`/students/${student.id}`}
                            className="border border-[#E8D8BD] bg-[#FFF8E7] px-2 py-1 text-[11px] font-semibold text-[#3B2921] hover:border-[#D96B27] hover:text-[#D96B27]"
                            style={{ borderRadius: "2px" }}
                          >
                            Profile
                          </Link>

                          <RoleGate roles={["admin"]}>
                            <Link
                              href={`/students/${student.id}/edit`}
                              className="border border-[#E8D8BD] bg-[#FFF8E7] px-2 py-1 text-[11px] font-semibold text-[#6B5A4A] hover:text-[#3B2921]"
                              style={{ borderRadius: "2px" }}
                            >
                              Edit
                            </Link>
                            <button
                              type="button"
                              onClick={() => handleDelete(student)}
                              disabled={deletingId === student.id}
                              className="border border-[#B94E27] bg-[#FFF8E7] px-2 py-1 text-[11px] font-semibold text-[#B94E27] hover:bg-[#B94E27] hover:text-white disabled:opacity-50"
                              style={{ borderRadius: "2px" }}
                            >
                              {deletingId === student.id ? "..." : "Delete"}
                            </button>
                          </RoleGate>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Pagination */}
          <div className="flex items-center justify-between border-t border-[#E8D8BD] bg-[#FFFDF5] px-4 py-3 text-xs text-[#6B5A4A]">
            <span>
              Page {page} ({filteredStudents.length} records shown)
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                disabled={page === 1}
                className="border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-1 font-semibold text-[#3B2921] hover:border-[#D96B27] disabled:opacity-40"
                style={{ borderRadius: "2px" }}
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((prev) => prev + 1)}
                disabled={studentList.length < pageSize}
                className="border border-[#E8D8BD] bg-[#FFF8E7] px-3 py-1 font-semibold text-[#3B2921] hover:border-[#D96B27] disabled:opacity-40"
                style={{ borderRadius: "2px" }}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}