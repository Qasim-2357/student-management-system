"use client"

import React, { useEffect, useMemo, useState } from "react"
import { useAuth } from "@/lib/hooks/use-auth"
import { useStudents } from "@/lib/hooks/use-students"
import { useStudentPerformance, useAnalyzeStudentPerformance } from "@/lib/hooks/use-performance"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { LoadingState } from "@/components/states/LoadingState"
import { ErrorState } from "@/components/states/ErrorState"
import { EmptyState } from "@/components/states/EmptyState"
import type { Student } from "@/lib/types/students"
import { useStudentCharts } from "@/lib/hooks/use-charts"

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
  const charts = useStudentCharts(activeStudentId)
  const analysis = useAnalyzeStudentPerformance()

  // A stale analysis for a previously-selected student should never be
  // shown against a different student's data - clear it whenever the
  // active student changes. This never triggers a fetch by itself.
  useEffect(() => {
    analysis.reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeStudentId])

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
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader><CardTitle className="text-base">Subject averages</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">{charts.marks.data?.data.length ? charts.marks.data.data.map((item) => <div key={item.subject_id} className="flex justify-between border-b py-2"><span>{item.subject_name}</span><span>{item.average_marks}</span></div>) : <p className="text-[#A89F91]">No subject chart data.</p>}</CardContent>
            </Card>
            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader><CardTitle className="text-base">Exam averages</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">{charts.exams.data?.data.length ? charts.exams.data.data.map((item) => <div key={item.exam_id} className="flex justify-between border-b py-2"><span>{item.exam_name}</span><span>{item.average_marks}</span></div>) : <p className="text-[#A89F91]">No exam chart data.</p>}</CardContent>
            </Card>
            <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
              <CardHeader><CardTitle className="text-base">Attendance summary</CardTitle></CardHeader>
              <CardContent>{charts.attendance.data ? <p className="text-sm">{charts.attendance.data.present} present / {charts.attendance.data.total} total ({charts.attendance.data.percentage}%)</p> : <p className="text-sm text-[#A89F91]">No attendance chart data.</p>}</CardContent>
            </Card>
          </div>

          <Card className="border-[#E8DCC4] bg-[#FFFDF9]">
            <CardHeader className="space-y-1">
              <CardTitle className="text-base font-semibold text-[#422006]">
                AI Performance Analysis
              </CardTitle>
              <p className="text-sm text-[#78350F]">
                An AI-generated interpretation of this student&apos;s existing academic
                performance above. The AI does not calculate any marks, grades, or
                attendance figures itself - it only summarizes the numbers already shown
                on this page.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysis.status === "idle" ? (
                <Button
                  onClick={() => activeStudentId && analysis.mutate(activeStudentId)}
                  disabled={!activeStudentId}
                >
                  Analyze Performance
                </Button>
              ) : analysis.status === "pending" ? (
                <div className="space-y-3">
                  <Button disabled>Analyzing…</Button>
                  <LoadingState label="Generating AI performance analysis" rows={4} />
                </div>
              ) : analysis.status === "error" ? (
                <ErrorState
                  title={analysis.error?.status === 503 ? "AI analysis unavailable" : "Analysis failed"}
                  message={
                    analysis.error?.status === 503
                      ? "AI analysis is currently unavailable. Please try again later."
                      : analysis.error?.message || "Something went wrong while analyzing performance."
                  }
                  onRetry={() => activeStudentId && analysis.mutate(activeStudentId)}
                />
              ) : (
                <div className="space-y-5">
                  <div>
                    <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                      Summary
                    </h3>
                    <p className="text-sm text-[#422006]">{analysis.data.summary}</p>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                        Strengths
                      </h3>
                      {analysis.data.strengths.length ? (
                        <ul className="list-disc space-y-1 pl-4 text-sm text-[#422006]">
                          {analysis.data.strengths.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-[#A89F91]">None identified.</p>
                      )}
                    </div>

                    <div>
                      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                        Areas for Improvement
                      </h3>
                      {analysis.data.areas_for_improvement.length ? (
                        <ul className="list-disc space-y-1 pl-4 text-sm text-[#422006]">
                          {analysis.data.areas_for_improvement.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-[#A89F91]">None identified.</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-[#A89F91]">
                      Recommendations
                    </h3>
                    {analysis.data.recommendations.length ? (
                      <ul className="list-disc space-y-1 pl-4 text-sm text-[#422006]">
                        {analysis.data.recommendations.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-[#A89F91]">No recommendations provided.</p>
                    )}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => activeStudentId && analysis.mutate(activeStudentId)}
                  >
                    Re-analyze
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}