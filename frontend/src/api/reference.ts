import { apiFetch } from './client'
import type { Commodity, Country, Market } from '../types'

export function getCountries(): Promise<Country[]> {
  return apiFetch('/countries')
}

export function getCommodities(): Promise<Commodity[]> {
  return apiFetch('/commodities')
}

export function getMarkets(country?: string): Promise<Market[]> {
  const params = country ? `?country=${encodeURIComponent(country)}` : ''
  return apiFetch(`/markets${params}`)
}
