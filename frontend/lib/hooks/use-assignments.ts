'use client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createAssignment, deleteAssignment, getAssignment, listAssignments, listSubmissions, updateAssignment } from '@/lib/api/assignments';
import { queryKeys } from '@/lib/query-keys';
import type { AssignmentCreate, AssignmentUpdate } from '@/lib/types/assignments';
export function useAssignments(params: Parameters<typeof listAssignments>[0] = {}) { return useQuery({ queryKey: queryKeys.assignments.list(params), queryFn: () => listAssignments(params) }); }
export function useAssignment(id: number) { return useQuery({ queryKey: queryKeys.assignments.detail(id), queryFn: () => getAssignment(id), enabled: id > 0 }); }
export function useAssignmentSubmissions(id: number) { return useQuery({ queryKey: queryKeys.assignments.submissions(id), queryFn: () => listSubmissions(id), enabled: id > 0 }); }
export function useCreateAssignment() { const qc = useQueryClient(); return useMutation({ mutationFn: (body: AssignmentCreate) => createAssignment(body), onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.assignments.all }) }); }
export function useUpdateAssignment(id: number) { const qc = useQueryClient(); return useMutation({ mutationFn: (body: AssignmentUpdate) => updateAssignment(id, body), onSuccess: (item) => { qc.setQueryData(queryKeys.assignments.detail(id), item); return qc.invalidateQueries({ queryKey: queryKeys.assignments.all }); } }); }
export function useDeleteAssignment() { const qc = useQueryClient(); return useMutation({ mutationFn: deleteAssignment, onSuccess: (_, id) => { qc.removeQueries({ queryKey: queryKeys.assignments.detail(id) }); return qc.invalidateQueries({ queryKey: queryKeys.assignments.all }); } }); }
