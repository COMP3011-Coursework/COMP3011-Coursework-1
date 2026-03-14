import { useEffect, useState } from 'react'
import { getCrisisScore, getTrends, getVolatility } from '../api/analytics'
import type { CrisisScore, TrendPoint, VolatilityItem } from '../types'
import PriceTrendChart from './PriceTrendChart'
import VolatilityList from './VolatilityList'

interface Props {
  iso3: string
  onClose: () => void
}

const severityColour: Record<string, string> = {
  stable: 'bg-green-100 text-green-800',
  moderate: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-500 mb-0.5">
        <span>{label}</span>
        <span>{value.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}

export default function CountryDetailPanel({ iso3, onClose }: Props) {
  const [score, setScore] = useState<CrisisScore | null>(null)
  const [trends, setTrends] = useState<TrendPoint[]>([])
  const [volatility, setVolatility] = useState<VolatilityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    let cancelled = false

    async function load() {
      try {
        const [crisisScore, vol] = await Promise.all([
          getCrisisScore(iso3),
          getVolatility(iso3, 10),
        ])
        if (cancelled) return
        setScore(crisisScore)
        setVolatility(vol.items)

        // Fetch trends for top volatile commodity if available
        if (vol.items.length > 0) {
          try {
            const trendData = await getTrends(iso3, vol.items[0].commodity_id)
            if (!cancelled) setTrends(trendData.points)
          } catch {
            // trends are optional
          }
        }
      } catch (err) {
        if (!cancelled) setError(String(err))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [iso3])

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h2 className="font-semibold text-gray-900">{iso3}</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-700 text-lg leading-none"
          aria-label="Close"
        >
          ×
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loading && (
          <div className="flex items-center justify-center h-32 text-gray-400 text-sm">
            Loading…
          </div>
        )}
        {error && <p className="text-red-500 text-sm">{error}</p>}

        {score && !loading && (
          <>
            <div className="flex items-center gap-3">
              <span className="text-3xl font-bold text-gray-900">
                {score.crisis_score.toFixed(1)}
              </span>
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${severityColour[score.severity]}`}
              >
                {score.severity}
              </span>
            </div>

            <div className="space-y-2">
              <ScoreBar label="Volatility" value={score.volatility_score} />
              <ScoreBar label="Trend" value={score.trend_score} />
              <ScoreBar label="Breadth" value={score.breadth_score} />
            </div>

            {trends.length > 0 && (
              <div>
                <p className="text-xs text-gray-500 mb-1">
                  Price trend — {volatility[0]?.commodity_name}
                </p>
                <PriceTrendChart points={trends} />
              </div>
            )}

            <div>
              <p className="text-xs text-gray-500 mb-2">Most volatile commodities</p>
              <VolatilityList items={volatility.slice(0, 5)} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
