import { apiFetch } from './client'
import type { CrisisScore, TrendResponse, VolatilityResponse } from '../types'

export function getCrisisScores(): Promise<CrisisScore[]> {
  return apiFetch('/analytics/crisis-scores')
}

export function getCrisisScore(country: string): Promise<CrisisScore> {
  return apiFetch(`/analytics/crisis-scores/${encodeURIComponent(country)}`)
}

export function getTrends(
  country: string,
  commodityId: number,
  dateFrom?: string,
  dateTo?: string,
): Promise<TrendResponse> {
  const params = new URLSearchParams({
    country,
    commodity_id: String(commodityId),
  })
  if (dateFrom) params.set('date_from', dateFrom)
  if (dateTo) params.set('date_to', dateTo)
  return apiFetch(`/analytics/trends?${params}`)
}

export function getVolatility(country: string, limit = 10): Promise<VolatilityResponse> {
  return apiFetch(`/analytics/volatility?country=${encodeURIComponent(country)}&limit=${limit}`)
}
