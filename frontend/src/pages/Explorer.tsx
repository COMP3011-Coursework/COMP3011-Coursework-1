import { useEffect, useState } from 'react'
import { getTrends } from '../api/analytics'
import { fetchPrices } from '../api/prices'
import { getCommodities, getCountries } from '../api/reference'
import PriceTrendChart from '../components/PriceTrendChart'
import type { Commodity, Country, Price, TrendPoint } from '../types'

export default function Explorer() {
  const [countries, setCountries] = useState<Country[]>([])
  const [commodities, setCommodities] = useState<Commodity[]>([])

  const [country, setCountry] = useState('')
  const [commodityId, setCommodityId] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(1)

  const [prices, setPrices] = useState<Price[]>([])
  const [total, setTotal] = useState(0)
  const [trendPoints, setTrendPoints] = useState<TrendPoint[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const PAGE_SIZE = 20

  useEffect(() => {
    Promise.all([getCountries(), getCommodities()]).then(([c, comms]) => {
      setCountries(c)
      setCommodities(comms)
      search(1)
    })
  }, [])

  async function search(p = 1) {
    setLoading(true)
    setError(null)
    try {
      const priceData = await fetchPrices({
        country: country || undefined,
        commodity_id: commodityId ? Number(commodityId) : undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        page: p,
        page_size: PAGE_SIZE,
      })
      setPrices(priceData.items)
      setTotal(priceData.total)
      setPage(p)

      if (country && commodityId) {
        const trendData = await getTrends(country, Number(commodityId), dateFrom || undefined, dateTo || undefined)
        setTrendPoints(trendData.points)
      } else {
        setTrendPoints([])
      }
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const commodityMap = new Map(commodities.map((c) => [c.id, c.name]))

  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto">
      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Filter Prices</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Country</label>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Select country…</option>
              {countries.map((c) => (
                <option key={c.countryiso3} value={c.countryiso3}>
                  {c.countryiso3}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Commodity</label>
            <select
              value={commodityId}
              onChange={(e) => setCommodityId(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Select commodity…</option>
              {commodities.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={() => search(1)}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading…' : 'Search'}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
      </div>

      {/* Trend chart */}
      {trendPoints.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-2">Price Trend</h2>
          <PriceTrendChart points={trendPoints} />
        </div>
      )}

      {/* Results table */}
      {prices.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {total.toLocaleString()} results
            </span>
            <div className="flex items-center gap-2 text-sm">
              <button
                onClick={() => search(page - 1)}
                disabled={page <= 1}
                className="px-2 py-0.5 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-50"
              >
                ‹ Prev
              </button>
              <span className="text-gray-500">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => search(page + 1)}
                disabled={page >= totalPages}
                className="px-2 py-0.5 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-50"
              >
                Next ›
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-3 py-2">Date</th>
                  <th className="px-3 py-2">Country</th>
                  <th className="px-3 py-2">Commodity</th>
                  <th className="px-3 py-2">Market</th>
                  <th className="px-3 py-2">Unit</th>
                  <th className="px-3 py-2 text-right">Price</th>
                  <th className="px-3 py-2 text-right">USD Price</th>
                  <th className="px-3 py-2">Currency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {prices.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-3 py-1.5 font-mono text-xs">{p.date}</td>
                    <td className="px-3 py-1.5">{p.countryiso3}</td>
                    <td className="px-3 py-1.5 text-gray-600">{commodityMap.get(p.commodity_id) ?? p.commodity_id}</td>
                    <td className="px-3 py-1.5 text-gray-600">{p.market_id}</td>
                    <td className="px-3 py-1.5 text-gray-600">{p.unit ?? '—'}</td>
                    <td className="px-3 py-1.5 text-right font-mono">
                      {p.price != null ? p.price.toFixed(2) : '—'}
                    </td>
                    <td className="px-3 py-1.5 text-right font-mono">
                      {p.usdprice != null ? `$${p.usdprice.toFixed(2)}` : '—'}
                    </td>
                    <td className="px-3 py-1.5 text-gray-600">{p.currency_code}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!loading && prices.length === 0 && (
        <div className="text-center text-gray-400 py-12 text-sm">
          No results. Try different filters.
        </div>
      )}
    </div>
  )
}
