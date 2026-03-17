import { useEffect, useState } from 'react'
import { login, register } from '../api/auth'
import { createPrice, deletePrice, fetchPrices, updatePrice } from '../api/prices'
import { getCommodities, getCountries, getCurrencies, getMarkets } from '../api/reference'
import { useAuth } from '../contexts/AuthContext'
import Spinner from '../components/Spinner'
import type { Commodity, Country, Currency, Market, Price } from '../types'
import { countryName } from '../utils/countryName'

// ── Auth form ─────────────────────────────────────────────────────────────────

function AuthForm() {
  const { login: setToken } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'register') {
        await register(username, email, password)
      }
      const token = await login(username, password)
      setToken(token.access_token, username)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        {mode === 'login' ? 'Log in' : 'Create account'}
      </h2>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        {mode === 'register' && (
          <div>
            <label className="block text-xs text-gray-500 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        )}
        <div>
          <label className="block text-xs text-gray-500 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Register & log in'}
        </button>
      </form>
      <button
        onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null) }}
        className="mt-3 text-xs text-blue-600 hover:underline w-full text-center"
      >
        {mode === 'login' ? 'No account? Register' : 'Have an account? Log in'}
      </button>
    </div>
  )
}

// ── Main data-entry form ──────────────────────────────────────────────────────

function PriceForm({ onCreated }: { onCreated: () => void }) {
  const { token } = useAuth()
  const [countries, setCountries] = useState<Country[]>([])
  const [commodities, setCommodities] = useState<Commodity[]>([])
  const [currencies, setCurrencies] = useState<Currency[]>([])
  const [markets, setMarkets] = useState<Market[]>([])

  const [country, setCountry] = useState('')
  const [commodityId, setCommodityId] = useState('')
  const [marketId, setMarketId] = useState('')
  const [date, setDate] = useState('')
  const [price, setPrice] = useState('')
  const [usdPrice, setUsdPrice] = useState('')
  const [currency, setCurrency] = useState('')
  const [unit, setUnit] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    Promise.all([getCountries(), getCommodities(), getCurrencies()]).then(([c, comms, currs]) => {
      setCountries(c)
      setCommodities(comms)
      setCurrencies(currs)
    })
  }, [])

  useEffect(() => {
    if (country) {
      getMarkets(country).then(setMarkets)
    } else {
      setMarkets([])
      setMarketId('')
    }
  }, [country])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!token) return
    setError(null)
    setSuccess(false)
    setLoading(true)
    try {
      await createPrice(
        {
          date,
          countryiso3: country,
          commodity_id: Number(commodityId),
          market_id: Number(marketId),
          currency_code: currency,
          price: price ? Number(price) : undefined,
          usdprice: usdPrice ? Number(usdPrice) : undefined,
          unit: unit || undefined,
        },
        token,
      )
      setSuccess(true)
      setDate('')
      setPrice('')
      setUsdPrice('')
      onCreated()
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className="bg-white rounded-lg border border-gray-200 p-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Add Price Entry</h2>
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Date *</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Country *</label>
          <select
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            required
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select…</option>
            {countries.map((c) => (
              <option key={c.countryiso3} value={c.countryiso3}>
                {countryName(c.countryiso3)} ({c.countryiso3})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Market *</label>
          <select
            value={marketId}
            onChange={(e) => setMarketId(e.target.value)}
            required
            disabled={!country}
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="">Select…</option>
            {markets.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Commodity *</label>
          <select
            value={commodityId}
            onChange={(e) => setCommodityId(e.target.value)}
            required
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select…</option>
            {commodities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Currency *</label>
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            required
            className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select…</option>
            {currencies.map((c) => (
              <option key={c.code} value={c.code}>{c.code} — {c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Local price</label>
          <input
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            min="0"
            step="any"
            className="border border-gray-300 rounded px-2 py-1.5 text-sm w-24 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">USD price</label>
          <input
            type="number"
            value={usdPrice}
            onChange={(e) => setUsdPrice(e.target.value)}
            min="0"
            step="any"
            className="border border-gray-300 rounded px-2 py-1.5 text-sm w-24 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Unit</label>
          <input
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="KG"
            className="border border-gray-300 rounded px-2 py-1.5 text-sm w-20 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving…' : 'Add Entry'}
        </button>
      </div>

      {success && <p className="mt-2 text-sm text-green-600">Entry added successfully.</p>}
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </form>
  )
}

// ── Entries table with inline CRUD ────────────────────────────────────────────

type Draft = {
  date: string
  countryiso3: string
  market_id: string
  commodity_id: string
  currency_code: string
  price: string
  usdprice: string
  unit: string
}

function toDraft(p: Price): Draft {
  return {
    date: p.date,
    countryiso3: p.countryiso3,
    market_id: String(p.market_id),
    commodity_id: String(p.commodity_id),
    currency_code: p.currency_code,
    price: p.price != null ? String(p.price) : '',
    usdprice: p.usdprice != null ? String(p.usdprice) : '',
    unit: p.unit ?? '',
  }
}

function EntriesTable({
  entries,
  loading,
  countries,
  commodities,
  currencies,
  allMarkets,
  commodityMap,
  marketMap,
  page,
  total,
  pageSize,
  onPageChange,
  onUpdate,
  onDelete,
}: {
  entries: Price[]
  loading: boolean
  countries: Country[]
  commodities: Commodity[]
  currencies: Currency[]
  allMarkets: Market[]
  commodityMap: Map<number, string>
  marketMap: Map<number, string>
  page: number
  total: number
  pageSize: number
  onPageChange: (p: number) => void
  onUpdate: (id: number, draft: Draft) => Promise<void>
  onDelete: (id: number) => void
}) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [draft, setDraft] = useState<Draft>({
    date: '', countryiso3: '', market_id: '', commodity_id: '',
    currency_code: '', price: '', usdprice: '', unit: '',
  })
  const [saving, setSaving] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  function startEdit(p: Price) {
    setEditingId(p.id)
    setDraft(toDraft(p))
    setEditError(null)
  }

  function cancelEdit() {
    setEditingId(null)
    setEditError(null)
  }

  async function saveEdit(id: number) {
    setSaving(true)
    setEditError(null)
    try {
      await onUpdate(id, draft)
      setEditingId(null)
    } catch (err) {
      setEditError(String(err))
    } finally {
      setSaving(false)
    }
  }

  const totalPages = Math.ceil(total / pageSize)
  const ci = 'border border-gray-300 rounded px-1.5 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500'

  // Markets for the country currently in the draft
  const draftMarkets = allMarkets.filter((m) => m.countryiso3 === draft.countryiso3)

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700">Entries</h2>
        <span className="text-xs text-gray-400">{total} total</span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Spinner />
        </div>
      ) : entries.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No entries yet.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Date</th>
                  <th className="px-3 py-2">Country</th>
                  <th className="px-3 py-2">Market</th>
                  <th className="px-3 py-2">Commodity</th>
                  <th className="px-3 py-2">Currency</th>
                  <th className="px-3 py-2 text-right">Local Price</th>
                  <th className="px-3 py-2 text-right">USD Price</th>
                  <th className="px-3 py-2">Unit</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {entries.map((p) => {
                  const isEditing = editingId === p.id
                  return (
                    <tr key={p.id} className={isEditing ? 'bg-blue-50' : 'hover:bg-gray-50'}>
                      <td className="px-3 py-1.5 font-mono text-xs text-gray-400">{p.id}</td>

                      {isEditing ? (
                        <>
                          <td className="px-2 py-1">
                            <input type="date" value={draft.date} onChange={(e) => setDraft({ ...draft, date: e.target.value })} className={ci} />
                          </td>
                          <td className="px-2 py-1">
                            <select
                              value={draft.countryiso3}
                              onChange={(e) => setDraft({ ...draft, countryiso3: e.target.value, market_id: '' })}
                              className={ci}
                            >
                              <option value="">—</option>
                              {countries.map((c) => (
                                <option key={c.countryiso3} value={c.countryiso3}>{countryName(c.countryiso3)} ({c.countryiso3})</option>
                              ))}
                            </select>
                          </td>
                          <td className="px-2 py-1">
                            <select
                              value={draft.market_id}
                              onChange={(e) => setDraft({ ...draft, market_id: e.target.value })}
                              disabled={!draft.countryiso3}
                              className={ci + ' disabled:opacity-50'}
                            >
                              <option value="">—</option>
                              {draftMarkets.map((m) => (
                                <option key={m.id} value={m.id}>{m.name}</option>
                              ))}
                            </select>
                          </td>
                          <td className="px-2 py-1">
                            <select
                              value={draft.commodity_id}
                              onChange={(e) => setDraft({ ...draft, commodity_id: e.target.value })}
                              className={ci}
                            >
                              <option value="">—</option>
                              {commodities.map((c) => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                              ))}
                            </select>
                          </td>
                          <td className="px-2 py-1">
                            <select value={draft.currency_code} onChange={(e) => setDraft({ ...draft, currency_code: e.target.value })} className={ci}>
                              <option value="">—</option>
                              {currencies.map((c) => (
                                <option key={c.code} value={c.code}>{c.code}</option>
                              ))}
                            </select>
                          </td>
                          <td className="px-2 py-1 text-right">
                            <input type="number" value={draft.price} onChange={(e) => setDraft({ ...draft, price: e.target.value })} min="0" step="any" className={ci + ' w-24 text-right'} />
                          </td>
                          <td className="px-2 py-1 text-right">
                            <input type="number" value={draft.usdprice} onChange={(e) => setDraft({ ...draft, usdprice: e.target.value })} min="0" step="any" className={ci + ' w-24 text-right'} />
                          </td>
                          <td className="px-2 py-1">
                            <input value={draft.unit} onChange={(e) => setDraft({ ...draft, unit: e.target.value })} className={ci + ' w-16'} />
                          </td>
                          <td className="px-3 py-1.5 text-right whitespace-nowrap">
                            <div className="flex gap-2 justify-end">
                              <button onClick={() => saveEdit(p.id)} disabled={saving} className="text-blue-600 hover:text-blue-800 text-xs font-medium disabled:opacity-50">
                                {saving ? 'Saving…' : 'Save'}
                              </button>
                              <button onClick={cancelEdit} className="text-gray-400 hover:text-gray-600 text-xs">Cancel</button>
                            </div>
                            {editError && <p className="text-red-500 text-xs mt-0.5">{editError}</p>}
                          </td>
                        </>
                      ) : (
                        <>
                          <td className="px-3 py-1.5 font-mono text-xs">{p.date}</td>
                          <td className="px-3 py-1.5">{p.countryiso3}</td>
                          <td className="px-3 py-1.5 text-gray-600">{marketMap.get(p.market_id) ?? p.market_id}</td>
                          <td className="px-3 py-1.5">{commodityMap.get(p.commodity_id) ?? p.commodity_id}</td>
                          <td className="px-3 py-1.5 text-gray-500">{p.currency_code}</td>
                          <td className="px-3 py-1.5 text-right font-mono">
                            {p.price != null ? p.price.toFixed(2) : '—'}
                          </td>
                          <td className="px-3 py-1.5 text-right font-mono">
                            {p.usdprice != null ? `$${p.usdprice.toFixed(2)}` : '—'}
                          </td>
                          <td className="px-3 py-1.5 text-gray-500">{p.unit ?? '—'}</td>
                          <td className="px-3 py-1.5 text-right whitespace-nowrap">
                            <div className="flex gap-2 justify-end">
                              <button onClick={() => startEdit(p)} className="text-blue-500 hover:text-blue-700 text-xs">Edit</button>
                              <button onClick={() => onDelete(p.id)} className="text-red-500 hover:text-red-700 text-xs">Delete</button>
                            </div>
                          </td>
                        </>
                      )}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-2 border-t border-gray-100 text-xs text-gray-500">
              <span>Page {page} of {totalPages}</span>
              <div className="flex gap-1">
                <button
                  onClick={() => onPageChange(page - 1)}
                  disabled={page <= 1}
                  className="px-2 py-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  ‹
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((n) => n === 1 || n === totalPages || Math.abs(n - page) <= 1)
                  .reduce<(number | '…')[]>((acc, n, i, arr) => {
                    if (i > 0 && (n as number) - (arr[i - 1] as number) > 1) acc.push('…')
                    acc.push(n)
                    return acc
                  }, [])
                  .map((item, i) =>
                    item === '…' ? (
                      <span key={`ellipsis-${i}`} className="px-2 py-1">…</span>
                    ) : (
                      <button
                        key={item}
                        onClick={() => onPageChange(item as number)}
                        className={`px-2 py-1 rounded border ${page === item ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-200 hover:bg-gray-50'}`}
                      >
                        {item}
                      </button>
                    )
                  )}
                <button
                  onClick={() => onPageChange(page + 1)}
                  disabled={page >= totalPages}
                  className="px-2 py-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  ›
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

const PAGE_SIZE = 10

export default function DataEntry() {
  const { token } = useAuth()
  const [entries, setEntries] = useState<Price[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [tableLoading, setTableLoading] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  // Reference data
  const [countries, setCountries] = useState<Country[]>([])
  const [commodities, setCommodities] = useState<Commodity[]>([])
  const [currencies, setCurrencies] = useState<Currency[]>([])
  const [allMarkets, setAllMarkets] = useState<Market[]>([])
  const [commodityMap, setCommodityMap] = useState<Map<number, string>>(new Map())
  const [marketMap, setMarketMap] = useState<Map<number, string>>(new Map())

  // Filters
  const [filterCountry, setFilterCountry] = useState('')
  const [filterCommodityId, setFilterCommodityId] = useState('')
  const [filterDateFrom, setFilterDateFrom] = useState('')
  const [filterDateTo, setFilterDateTo] = useState('')

  useEffect(() => {
    Promise.all([getCountries(), getCommodities(), getCurrencies(), getMarkets()]).then(([ctrs, comms, currs, mkts]) => {
      setCountries(ctrs)
      setCommodities(comms)
      setCurrencies(currs)
      setAllMarkets(mkts)
      setCommodityMap(new Map(comms.map((c) => [c.id, c.name])))
      setMarketMap(new Map(mkts.map((m) => [m.id, m.name])))
    })
  }, [])

  async function loadPage(p: number) {
    setTableLoading(true)
    try {
      const data = await fetchPrices({
        country: filterCountry || undefined,
        commodity_id: filterCommodityId ? Number(filterCommodityId) : undefined,
        date_from: filterDateFrom || undefined,
        date_to: filterDateTo || undefined,
        page: p,
        page_size: PAGE_SIZE,
      })
      setEntries(data.items)
      setTotal(data.total)
      setPage(p)
    } catch {
      // silently fail — not critical
    } finally {
      setTableLoading(false)
    }
  }

  useEffect(() => {
    if (token) loadPage(1)
  }, [token])

  async function handleUpdate(id: number, draft: Draft) {
    if (!token) return
    const updated = await updatePrice(
      id,
      {
        date: draft.date || undefined,
        countryiso3: draft.countryiso3 || undefined,
        market_id: draft.market_id ? Number(draft.market_id) : undefined,
        commodity_id: draft.commodity_id ? Number(draft.commodity_id) : undefined,
        currency_code: draft.currency_code || undefined,
        price: draft.price ? Number(draft.price) : undefined,
        usdprice: draft.usdprice ? Number(draft.usdprice) : undefined,
        unit: draft.unit || undefined,
      },
      token,
    )
    setEntries((prev) => prev.map((e) => (e.id === id ? updated : e)))
  }

  async function handleDelete(id: number) {
    if (!token) return
    setDeleteError(null)
    try {
      await deletePrice(id, token)
      await loadPage(page)
    } catch (err) {
      setDeleteError(String(err))
    }
  }

  if (!token) {
    return <AuthForm />
  }

  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto">
      <PriceForm onCreated={() => loadPage(1)} />

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Filter</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Country</label>
            <select
              value={filterCountry}
              onChange={(e) => setFilterCountry(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All</option>
              {countries.map((c) => (
                <option key={c.countryiso3} value={c.countryiso3}>{countryName(c.countryiso3)} ({c.countryiso3})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Commodity</label>
            <select
              value={filterCommodityId}
              onChange={(e) => setFilterCommodityId(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All</option>
              {commodities.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Date from</label>
            <input
              type="date"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Date to</label>
            <input
              type="date"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => loadPage(1)}
            className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-700"
          >
            Apply
          </button>
          <button
            onClick={() => {
              setFilterCountry('')
              setFilterCommodityId('')
              setFilterDateFrom('')
              setFilterDateTo('')
            }}
            className="text-gray-500 hover:text-gray-700 text-sm px-2 py-1.5"
          >
            Clear
          </button>
        </div>
      </div>

      {deleteError && <p className="text-sm text-red-500">{deleteError}</p>}

      <EntriesTable
        entries={entries}
        loading={tableLoading}
        countries={countries}
        commodities={commodities}
        currencies={currencies}
        allMarkets={allMarkets}
        commodityMap={commodityMap}
        marketMap={marketMap}
        page={page}
        total={total}
        pageSize={PAGE_SIZE}
        onPageChange={loadPage}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
      />
    </div>
  )
}
