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
};
