'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { useClasses } from '@/lib/hooks/use-classes';
import { useSubjects } from '@/lib/hooks/use-subjects';
import { useTeachers } from '@/lib/hooks/use-teachers';
import {
  useTeacherRelationships,
  useUpdateTeacherRelationships,
  useClassSubjects,
  useUpdateClassSubjects,
} from '@/lib/hooks/use-relationships';

export default function RelationshipsPage() {
  const teachers = useTeachers({ page: 1, page_size: 100 });
  const classes = useClasses({ page: 1, page_size: 100 });
  const subjects = useSubjects({ page: 1, page_size: 100 });

  const [teacherId, setTeacherId] = useState(0);
  const [classId, setClassId] = useState(0);

  // null means "use the values from the API".
  // Once the user changes a checkbox, these become the unsaved draft values.
  const [teacherClassesDraft, setTeacherClassesDraft] = useState<number[] | null>(null);
  const [teacherSubjectsDraft, setTeacherSubjectsDraft] = useState<number[] | null>(null);
  const [classSubjectsDraft, setClassSubjectsDraft] = useState<number[] | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const teacherRelationships = useTeacherRelationships(teacherId);
  const classRelationships = useClassSubjects(classId);

  const saveTeacher = useUpdateTeacherRelationships(teacherId);
  const saveClass = useUpdateClassSubjects(classId);

  if (
    teachers.isLoading ||
    classes.isLoading ||
    subjects.isLoading
  ) {
    return (
      <LoadingState
        label="Loading relationships"
        rows={4}
      />
    );
  }

  if (
    teachers.isError ||
    classes.isError ||
    subjects.isError
  ) {
    return (
      <ErrorState
        title="Relationships unavailable"
        message="The relationship lists could not be loaded."
      />
    );
  }

  const teacherClasses =
    teacherClassesDraft ?? teacherRelationships.data?.class_ids ?? [];

  const teacherSubjects =
    teacherSubjectsDraft ?? teacherRelationships.data?.subject_ids ?? [];

  const classSubjects =
    classSubjectsDraft ?? classRelationships.data?.subject_ids ?? [];

  const toggle = (values: number[], value: number) =>
    values.includes(value)
      ? values.filter((item) => item !== value)
      : [...values, value];

  const handleTeacherChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    const id = Number(event.target.value);

    setTeacherId(id);

    // New teacher = start with that teacher's API data.
    setTeacherClassesDraft(null);
    setTeacherSubjectsDraft(null);
  };

  const handleClassChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    const id = Number(event.target.value);

    setClassId(id);

    // New class = start with that class's API data.
    setClassSubjectsDraft(null);
  };

  const errorMessage = (error: unknown) =>
    error instanceof Error ? error.message : 'Unable to save relationship changes.';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-bold">
          Academic relationships
        </h1>
        <p className="text-sm text-muted-foreground">
          Assign teachers to classes and subjects, and subjects to classes.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Teacher assignments</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <Select
            value={teacherId || ''}
            onChange={handleTeacherChange}
          >
            <option value="">Select a teacher</option>

            {teachers.data?.items.map((teacher) => (
              <option key={teacher.id} value={teacher.id}>
                {teacher.name}
              </option>
            ))}
          </Select>

          {teacherId ? (
            <>
              <label className="block text-sm font-medium">
                Classes
              </label>

              <div className="grid gap-2 sm:grid-cols-2">
                {classes.data?.items.map((item) => (
                  <label
                    key={item.id}
                    className="flex items-center gap-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={teacherClasses.includes(item.id)}
                      onChange={() =>
                        setTeacherClassesDraft(
                          toggle(teacherClasses, item.id),
                        )
                      }
                    />

                    {item.name} ({item.code})
                  </label>
                ))}
              </div>

              <label className="block text-sm font-medium">
                Subjects
              </label>

              <div className="grid gap-2 sm:grid-cols-2">
                {subjects.data?.items.map((item) => (
                  <label
                    key={item.id}
                    className="flex items-center gap-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={teacherSubjects.includes(item.id)}
                      onChange={() =>
                        setTeacherSubjectsDraft(
                          toggle(teacherSubjects, item.id),
                        )
                      }
                    />

                    {item.name} ({item.code})
                  </label>
                ))}
              </div>

              <Button
                type="button"
                disabled={saveTeacher.isPending}
                onClick={() => {
                  setSaveMessage(null);
                  setSaveError(null);
                  saveTeacher.mutate({
                    teacher_id: teacherId,
                    class_ids: teacherClasses,
                    subject_ids: teacherSubjects,
                  }, {
                    onSuccess: () => {
                      setTeacherClassesDraft(null);
                      setTeacherSubjectsDraft(null);
                      setSaveMessage('Teacher assignments saved.');
                    },
                    onError: (error) => setSaveError(errorMessage(error)),
                  });
                }}
              >
                {saveTeacher.isPending ? 'Saving...' : 'Save teacher assignments'}
              </Button>
            </>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Class subjects</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <Select
            value={classId || ''}
            onChange={handleClassChange}
          >
            <option value="">Select a class</option>

            {classes.data?.items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} ({item.code})
              </option>
            ))}
          </Select>

          {classId ? (
            <>
              <div className="grid gap-2 sm:grid-cols-2">
                {subjects.data?.items.map((item) => (
                  <label
                    key={item.id}
                    className="flex items-center gap-2 text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={classSubjects.includes(item.id)}
                      onChange={() =>
                        setClassSubjectsDraft(
                          toggle(classSubjects, item.id),
                        )
                      }
                    />

                    {item.name} ({item.code})
                  </label>
                ))}
              </div>

              <Button
                type="button"
                disabled={saveClass.isPending}
                onClick={() => {
                  setSaveMessage(null);
                  setSaveError(null);
                  saveClass.mutate(classSubjects, {
                    onSuccess: () => {
                      setClassSubjectsDraft(null);
                      setSaveMessage('Class subjects saved.');
                    },
                    onError: (error) => setSaveError(errorMessage(error)),
                  });
                }}
              >
                {saveClass.isPending ? 'Saving...' : 'Save class subjects'}
              </Button>
            </>
          ) : null}
        </CardContent>
      </Card>
      {saveMessage ? <p className="text-sm text-green-700">{saveMessage}</p> : null}
      {saveError ? <p className="text-sm text-destructive">{saveError}</p> : null}
    </div>
  );
}