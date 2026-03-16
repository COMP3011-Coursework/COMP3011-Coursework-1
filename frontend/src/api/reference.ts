import { apiFetch } from './client'
import type { Commodity, Country, Currency, Market } from '../types'

export function getCountries(): Promise<Country[]> {
  return apiFetch('/countries')
}

export function getCommodities(): Promise<Commodity[]> {
  return apiFetch('/commodities')
}

export function getCurrencies(): Promise<Currency[]> {
  return apiFetch('/currencies')
}

export function getMarkets(country?: string): Promise<Market[]> {
  const params = country ? `?country=${encodeURIComponent(country)}` : ''
  return apiFetch(`/markets${params}`)
}
