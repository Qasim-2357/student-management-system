import { apiFetch } from '@/lib/api/client';
import type { Fee, FeeCreate, FeeListResponse, FeeReceipt, FeeUpdate } from '@/lib/types/fees';

export function listFees(params: { page?: number; page_size?: number; search?: string; student_id?: number; status?: string; due_date?: string } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== '') query.set(key, String(value)); });
  return apiFetch<FeeListResponse>(`/fees?${query}`);
}
export const getFee = (id: number) => apiFetch<Fee>(`/fees/${id}`);
export const createFee = (body: FeeCreate) => apiFetch<Fee>('/fees', { method: 'POST', body });
export const updateFee = (id: number, body: FeeUpdate) => apiFetch<Fee>(`/fees/${id}`, { method: 'PATCH', body });
export const deleteFee = (id: number) => apiFetch<void>(`/fees/${id}`, { method: 'DELETE' });
export const getFeeReceipt = (id: number) => apiFetch<FeeReceipt>(`/fees/${id}/receipt`);
