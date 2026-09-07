from pydantic import BaseModel, Field


class RelationshipIds(BaseModel):
    ids: list[int] = Field(default_factory=list)


class TeacherRelationshipsResponse(BaseModel):
    teacher_id: int
    class_ids: list[int]
    subject_ids: list[int]


class ClassSubjectsResponse(BaseModel):
    class_id: int
    subject_ids: list[int]
