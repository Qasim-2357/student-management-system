"""AI-powered interpretation of a student's already-calculated performance.

Design notes (see Day 13 requirements):

- This module never calculates marks, grades, attendance percentages, or
  fees itself. It reuses the existing, authoritative business logic in
  ``app.services.performance`` and ``app.services.attendance_reports`` to
  gather already-computed statistics, and only asks the AI to *interpret*
  them (summary / strengths / areas for improvement / recommendations).
- All network access to the AI provider goes through
  ``app.services.ai_provider.call_ai_provider`` - this module never talks
  to the provider directly, and routers never talk to the provider at all.
- Authorization is handled by the router via the existing
  ``authorize_student_access`` dependency, exactly like every other
  student-scoped endpoint. This module assumes the caller is already
  authorized.
"""

from __future__ import annotations

import json

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.schemas.ai_analysis import (
    AIPerformanceAnalysisResponse,
    AIStudentPerformanceSnapshot,
    AISubjectSnapshot,
)
from app.services.ai_provider import AIProviderError, call_ai_provider
from app.services.attendance_reports import get_student_attendance_report
from app.services.performance import get_student_performance


def build_student_performance_snapshot(
    db: Session, student_id: int
) -> AIStudentPerformanceSnapshot:
    """Gather the already-calculated, authoritative facts about a student
    that the AI is allowed to see and interpret. No statistic here is
    computed by this function - it is only assembled from existing
    business logic.
    """
    performance = get_student_performance(db, student_id)
    attendance = get_student_attendance_report(db, student_id)

    return AIStudentPerformanceSnapshot(
        student_id=performance.student_id,
        total_subjects=performance.total_subjects,
        percentage=performance.percentage,
        average_marks=performance.average_marks,
        overall_grade=performance.grade,
        subjects=[
            AISubjectSnapshot(
                subject_id=item.subject_id,
                exam_id=item.exam_id,
                marks=item.marks,
                grade=item.grade,
            )
            for item in performance.results
        ],
        attendance_percentage=attendance.summary.attendance_percentage,
    )


def _build_prompt(snapshot: AIStudentPerformanceSnapshot) -> str:
    data = snapshot.model_dump()
    return (
        "You are an academic performance analyst. You will be given "
        "already-calculated, authoritative statistics for one student. "
        "Do not recalculate or contradict any numbers - only interpret "
        "them.\n\n"
        f"Student performance data (JSON):\n{json.dumps(data)}\n\n"
        "Respond with ONLY a single JSON object (no prose, no markdown "
        "fences) with exactly these keys:\n"
        '  "summary": a short overall summary string,\n'
        '  "strengths": an array of short strings,\n'
        '  "areas_for_improvement": an array of short strings,\n'
        '  "recommendations": an array of short, actionable strings.\n'
    )


def _parse_ai_response(raw_text: str) -> AIPerformanceAnalysisResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned a malformed response",
        ) from exc

    try:
        return AIPerformanceAnalysisResponse.model_validate(parsed)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned a response that did not match the expected format",
        ) from exc


def get_student_ai_performance_analysis(
    db: Session, student_id: int
) -> AIPerformanceAnalysisResponse:
    """Produce an AI-generated interpretation of a student's performance.

    Assumes the caller has already authorized access to ``student_id``.
    """
    snapshot = build_student_performance_snapshot(db, student_id)
    prompt = _build_prompt(snapshot)

    try:
        raw_text = call_ai_provider(prompt)
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis is currently unavailable. Please try again later.",
        ) from exc

    return _parse_ai_response(raw_text)
