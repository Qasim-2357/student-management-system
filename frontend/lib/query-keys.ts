export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  students: {
    all: ['students'] as const,
    list: (params: unknown) => ['students', 'list', params] as const,
    detail: (id: number) => ['students', 'detail', id] as const,
  },
};
