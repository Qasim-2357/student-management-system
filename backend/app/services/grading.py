GRADE_THRESHOLDS = (
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0, "F"),
)


def calculate_grade(marks: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if marks >= threshold:
            return grade
    return "F"
