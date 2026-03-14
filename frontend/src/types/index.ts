export interface CrisisScore {
  countryiso3: string
  crisis_score: number
  severity: 'stable' | 'moderate' | 'high' | 'critical'
  volatility_score: number
  trend_score: number
  breadth_score: number
}

export interface TrendPoint {
  date: string
  avg_usdprice: number
  count: number
}

export interface TrendResponse {
  country: string
  commodity_id: number
  points: TrendPoint[]
}

export interface VolatilityItem {
  commodity_id: number
  commodity_name: string
  cv: number
  avg_usdprice: number
}

export interface VolatilityResponse {
  country: string
  items: VolatilityItem[]
}

export interface Price {
  id: number
  date: string
  countryiso3: string
  admin1: string | null
  admin2: string | null
  market_id: number
  commodity_id: number
  category: string | null
  unit: string | null
  priceflag: string | null
  pricetype: string | null
  currency_code: string
  price: number | null
  usdprice: number | null
  created_at: string
  updated_at: string
}

export interface PriceListResponse {
  items: Price[]
  total: number
  page: number
  page_size: number
}

export interface PriceCreate {
  date: string
  countryiso3: string
  market_id: number
  commodity_id: number
  currency_code: string
  price?: number
  usdprice?: number
  unit?: string
}

export interface Commodity {
  id: number
  category: string
  name: string
}

export interface Market {
  id: number
  name: string
  countryiso3: string
  admin1: string | null
  admin2: string | null
  latitude: number | null
  longitude: number | null
}

export interface Country {
  countryiso3: string
  count: number
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface RegionalItem {
  countryiso3: string
  avg_usdprice: number
  count: number
}
