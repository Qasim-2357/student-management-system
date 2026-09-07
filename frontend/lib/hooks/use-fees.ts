'use client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createFee, deleteFee, getFee, getFeeReceipt, listFees, updateFee } from '@/lib/api/fees';
import { queryKeys } from '@/lib/query-keys';
import type { FeeCreate, FeeUpdate } from '@/lib/types/fees';
export function useFees(params: Parameters<typeof listFees>[0] = {}) { return useQuery({ queryKey: queryKeys.fees.list(params), queryFn: () => listFees(params) }); }
export function useFee(id: number) { return useQuery({ queryKey: queryKeys.fees.detail(id), queryFn: () => getFee(id), enabled: id > 0 }); }
export function useFeeReceipt(id: number) { return useQuery({ queryKey: queryKeys.fees.receipt(id), queryFn: () => getFeeReceipt(id), enabled: id > 0 }); }
export function useCreateFee() { const qc = useQueryClient(); return useMutation({ mutationFn: (body: FeeCreate) => createFee(body), onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.fees.all }) }); }
export function useUpdateFee(id: number) { const qc = useQueryClient(); return useMutation({ mutationFn: (body: FeeUpdate) => updateFee(id, body), onSuccess: (item) => { qc.setQueryData(queryKeys.fees.detail(id), item); return qc.invalidateQueries({ queryKey: queryKeys.fees.all }); } }); }
export function useDeleteFee() { const qc = useQueryClient(); return useMutation({ mutationFn: deleteFee, onSuccess: (_, id) => { qc.removeQueries({ queryKey: queryKeys.fees.detail(id) }); return qc.invalidateQueries({ queryKey: queryKeys.fees.all }); } }); }
