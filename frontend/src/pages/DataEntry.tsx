import { useEffect, useState } from 'react'
import { login, register } from '../api/auth'
import { createPrice, deletePrice, fetchPrices } from '../api/prices'
import { getCommodities, getCountries, getMarkets } from '../api/reference'
import { useAuth } from '../contexts/AuthContext'
import type { Commodity, Country, Market, Price } from '../types'

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
    Promise.all([getCountries(), getCommodities()]).then(([c, comms]) => {
      setCountries(c)
      setCommodities(comms)
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
                {c.countryiso3}
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
          <input
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            placeholder="USD"
            required
            maxLength={3}
            className="border border-gray-300 rounded px-2 py-1.5 text-sm w-20 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
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

// ── Recent entries table ──────────────────────────────────────────────────────

function RecentEntries({
  entries,
  onDelete,
}: {
  entries: Price[]
  onDelete: (id: number) => void
}) {
  if (entries.length === 0) {
    return <p className="text-sm text-gray-400 text-center py-8">No entries yet.</p>
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-2 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700">Recent Entries</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
              <th className="px-3 py-2">ID</th>
              <th className="px-3 py-2">Date</th>
              <th className="px-3 py-2">Country</th>
              <th className="px-3 py-2">Commodity</th>
              <th className="px-3 py-2 text-right">USD Price</th>
              <th className="px-3 py-2">Currency</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {entries.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-3 py-1.5 font-mono text-xs text-gray-400">{p.id}</td>
                <td className="px-3 py-1.5 font-mono text-xs">{p.date}</td>
                <td className="px-3 py-1.5">{p.countryiso3}</td>
                <td className="px-3 py-1.5">{p.commodity_id}</td>
                <td className="px-3 py-1.5 text-right font-mono">
                  {p.usdprice != null ? `$${p.usdprice.toFixed(2)}` : '—'}
                </td>
                <td className="px-3 py-1.5 text-gray-500">{p.currency_code}</td>
                <td className="px-3 py-1.5 text-right">
                  <button
                    onClick={() => onDelete(p.id)}
                    className="text-red-500 hover:text-red-700 text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DataEntry() {
  const { token } = useAuth()
  const [entries, setEntries] = useState<Price[]>([])
  const [deleteError, setDeleteError] = useState<string | null>(null)

  async function loadRecent() {
    try {
      const data = await fetchPrices({ page: 1, page_size: 10 })
      setEntries(data.items)
    } catch {
      // silently fail — not critical
    }
  }

  useEffect(() => {
    if (token) loadRecent()
  }, [token])

  async function handleDelete(id: number) {
    if (!token) return
    setDeleteError(null)
    try {
      await deletePrice(id, token)
      setEntries((prev) => prev.filter((e) => e.id !== id))
    } catch (err) {
      setDeleteError(String(err))
    }
  }

  if (!token) {
    return <AuthForm />
  }

  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto">
      <PriceForm onCreated={loadRecent} />
      {deleteError && <p className="text-sm text-red-500">{deleteError}</p>}
      <RecentEntries entries={entries} onDelete={handleDelete} />
    </div>
  )
}
