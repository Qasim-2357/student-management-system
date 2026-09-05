from typing import Dict, NamedTuple, Optional


class GradeInfo(NamedTuple):
    percentage: float
    grade: str
    grade_point: float
    remarks: str


GRADE_THRESHOLDS: Dict[str, float] = {
    "A+": 90.0,
    "A": 80.0,
    "B": 70.0,
    "C": 60.0,
    "D": 50.0,
    "F": 0.0,
}

GRADE_POINTS: Dict[str, float] = {
    "A+": 10.0,
    "A": 9.0,
    "B": 8.0,
    "C": 7.0,
    "D": 6.0,
    "F": 0.0,
}

GRADE_REMARKS: Dict[str, str] = {
    "A+": "Outstanding",
    "A": "Excellent",
    "B": "Very Good",
    "C": "Good",
    "D": "Pass",
    "F": "Fail",
}


def calculate_grade(marks: float, max_marks: Optional[float] = None) -> str:
    if max_marks is not None and max_marks > 0:
        score = (marks / max_marks) * 100.0
    else:
        score = float(marks)

    for grade, threshold in GRADE_THRESHOLDS.items():
        if score >= threshold:
            return grade
    return "F"


def calculate_grade_info(marks: float, max_marks: Optional[float] = None) -> GradeInfo:
    if max_marks is not None and max_marks > 0:
        score = round((marks / max_marks) * 100.0, 2)
    else:
        score = round(float(marks), 2)

    grade = calculate_grade(score)
    gp = GRADE_POINTS.get(grade, 0.0)
    remarks = GRADE_REMARKS.get(grade, "Fail" if grade == "F" else "Pass")
    return GradeInfo(percentage=score, grade=grade, grade_point=gp, remarks=remarks)