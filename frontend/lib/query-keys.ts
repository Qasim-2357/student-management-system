export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  students: {
    all: ['students'] as const,
    list: (params: unknown) => ['students', 'list', params] as const,
    detail: (id: number) => ['students', 'detail', id] as const,
  },
  teachers: {
    all: ['teachers'] as const,
    list: (params: unknown) => ['teachers', 'list', params] as const,
    detail: (id: number) => ['teachers', 'detail', id] as const,
  },
  classes: {
    all: ['classes'] as const,
    list: (params: unknown) => ['classes', 'list', params] as const,
    detail: (id: number) => ['classes', 'detail', id] as const,
  },
  subjects: {
    all: ['subjects'] as const,
    list: (params: unknown) => ['subjects', 'list', params] as const,
    detail: (id: number) => ['subjects', 'detail', id] as const,
  },
  exams: {
    all: ['exams'] as const,
    list: (params: unknown) => ['exams', 'list', params] as const,
    detail: (id: number) => ['exams', 'detail', id] as const,
  },
  attendance: {
    all: ['attendance'] as const,
    list: (params: unknown) => ['attendance', 'list', params] as const,
    detail: (id: number) => ['attendance', 'detail', id] as const,
  },
  marks: {
    all: ['marks'] as const,
    list: (params: unknown) => ['marks', 'list', params] as const,
    detail: (id: number) => ['marks', 'detail', id] as const,
  },
  performance: {
    all: ["performance"] as const,
    student: (id: number) => ["performance", "student", id] as const,
  },
}
