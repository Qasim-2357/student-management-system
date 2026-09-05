"use client"

import React, { useMemo, useState } from "react"
import { useAuth } from "@/lib/hooks/use-auth"
import { useStudents } from "@/lib/hooks/use-students"
import { useStudentPerformance } from "@/lib/hooks/use-performance"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import { LoadingState } from "@/components/states/LoadingState"
import { ErrorState } from "@/components/states/ErrorState"
import { EmptyState } from "@/components/states/EmptyState"
import type { Student } from "@/lib/types/students"

export default function PerformanceDashboardPage() {
  const { user, isLoading: authLoading } = useAuth()
  const role = user?.role
  const isStudent = role === "student"
  const { data: studentsData, isLoading: studentsLoading, isError: studentsError, refetch: refetchStudents } = useStudents({})
  const [selectedStudentId, setSelectedStudentId] = useState<number | undefined>(undefined)

  const studentList = useMemo(() => studentsData?.items ?? [], [studentsData])
  const activeStudentId = useMemo(() => {
    if (isStudent) return studentList[0]?.id
    return selectedStudentId ?? studentList[0]?.id
  }, [isStudent, selectedStudentId, studentList])
  const performance = useStudentPerformance(activeStudentId)

  if (authLoading || studentsLoading) {
    return <LoadingState />
  }

  if (studentsError) {
    return <ErrorState message="Unable to load students." onRetry={() => refetchStudents()} />
  }

  if (studentList.length === 0) {
    return (
      <EmptyState
        title="No students available"
        description={isStudent ? "Your student profile could not be found." : "There are no authorized students to review."}
      />
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-serif text-2xl font-bold tracking-tight text-[#422006]">
            Academic Performance
          </h1>
          <p className="text-sm text-[#78350F]">
            Performance analytics and grading metrics.
          </p>
        </div>

        {!isStudent && (
          <div className="w-full sm:w-64">
            <Select
              value={activeStudentId}
              onChange={(event) => setSelectedStudentId(Number(event.target.value))}
              aria-label="Select student"
            >
              {studentList.map((student: Student) => (
                <option key={student.id} value={student.id}>
                  {student.name} ({student.roll_number})
                </option>
              ))}
            </Select>
          </div>
        )}
      </div>

      {performance.isLoading ? (
        <LoadingState />
      ) : performance.isError ? (
        <ErrorState
          message={performance.error?.message || "Failed to load performance metrics."}
          onRetry={() => performance.refetch()}
        />
      ) : !performance.data ? (
        <EmptyState title="No performance records" description="No performance history found for this student." />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                  Overall Grade
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span className="font-serif text-3xl font-bold text-[#D97706]">
                  {performance.data.grade}
                </span>
              </CardContent>
            </Card>

            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                  Percentage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-[#422006]">{performance.data.percentage}%</div>
              </CardContent>
            </Card>

            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                  Marks Obtained
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-[#422006]">{performance.data.marks_obtained}</div>
                <div className="text-xs text-[#78350F]">of {performance.data.total_marks}</div>
              </CardContent>
            </Card>

            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                  Average Marks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-[#422006]">{performance.data.average_marks}</div>
              </CardContent>
            </Card>

            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                  Total Subjects
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-[#422006]">{performance.data.total_subjects}</div>
              </CardContent>
            </Card>
          </div>

          <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-[#422006]">
                Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              {performance.data.results.length === 0 ? (
                <div className="py-12 text-center text-sm text-[#A89F91]">
                  No examination results recorded.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[640px] text-left text-sm">
                    <caption className="sr-only">Performance results</caption>
                    <thead className="border-b border-[#E8DCC4] text-xs uppercase tracking-wider text-[#A89F91]">
                      <tr>
                        <th className="px-4 py-3">Exam ID</th>
                        <th className="px-4 py-3">Subject ID</th>
                        <th className="px-4 py-3">Marks</th>
                        <th className="px-4 py-3">Grade</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#F5EFE6] text-[#422006]">
                      {performance.data.results.map((result) => (
                        <tr key={result.mark_id} className="hover:bg-[#FAF6F0]">
                          <td className="px-4 py-3">{result.exam_id}</td>
                          <td className="px-4 py-3">{result.subject_id}</td>
                          <td className="px-4 py-3">{result.marks}</td>
                          <td className="px-4 py-3 font-semibold text-[#D97706]">{result.grade}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
