export interface TeacherRelationships {
  teacher_id: number;
  class_ids: number[];
  subject_ids: number[];
}

export interface ClassSubjects {
  class_id: number;
  subject_ids: number[];
}
