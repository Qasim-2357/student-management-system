from pydantic import BaseModel, Field


class AIPerformanceAnalysisResponse(BaseModel):
    """Contract for the AI-generated interpretation of a student's
    already-calculated performance data.

    The AI is only ever asked to *interpret* structured, authoritative
    numbers produced by existing business logic (see
    ``app.services.ai_analysis``); it never computes marks, grades,
    attendance percentages, or fees itself.
    """

    summary: str
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class AISubjectSnapshot(BaseModel):
    """One row of already-calculated, authoritative subject performance
    handed to the AI for interpretation."""

    subject_id: int
    exam_id: int
    marks: float
    grade: str


class AIStudentPerformanceSnapshot(BaseModel):
    """The structured, pre-calculated facts sent to the AI provider.

    Every field here is sourced from existing business logic
    (``app.services.performance`` / ``app.services.attendance_reports``);
    the AI never derives or overrides these figures.
    """

    student_id: int
    total_subjects: int
    percentage: float
    average_marks: float
    overall_grade: str
    subjects: list[AISubjectSnapshot]
    attendance_percentage: float | None = None
