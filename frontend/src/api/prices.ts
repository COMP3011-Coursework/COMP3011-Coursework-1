import { apiFetch } from './client'
import type { Price, PriceCreate, PriceListResponse } from '../types'

export interface PriceFilters {
  country?: string
  commodity_id?: number
  market_id?: number
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
}

export function fetchPrices(filters: PriceFilters = {}): Promise<PriceListResponse> {
  const params = new URLSearchParams()
  if (filters.country) params.set('country', filters.country)
  if (filters.commodity_id) params.set('commodity_id', String(filters.commodity_id))
  if (filters.market_id) params.set('market_id', String(filters.market_id))
  if (filters.date_from) params.set('date_from', filters.date_from)
  if (filters.date_to) params.set('date_to', filters.date_to)
  params.set('page', String(filters.page ?? 1))
  params.set('page_size', String(filters.page_size ?? 20))
  return apiFetch(`/prices?${params}`)
}

export function createPrice(data: PriceCreate, token: string): Promise<Price> {
  return apiFetch('/prices', { method: 'POST', body: JSON.stringify(data) }, token)
}

export function updatePrice(id: number, data: Partial<PriceCreate>, token: string): Promise<Price> {
  return apiFetch(`/prices/${id}`, { method: 'PUT', body: JSON.stringify(data) }, token)
}

export function deletePrice(id: number, token: string): Promise<void> {
  return apiFetch(`/prices/${id}`, { method: 'DELETE' }, token)
}
