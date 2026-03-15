import { useState } from 'react'
import { getCrisisScores } from '../api/analytics'
import ChoroplethMap from '../components/ChoroplethMap'
import CountryDetailPanel from '../components/CountryDetailPanel'
import { useApi } from '../hooks/useApi'

export default function Dashboard() {
  const { data: scores, loading, error } = useApi(getCrisisScores)
  const [selectedIso3, setSelectedIso3] = useState<string | null>(null)
  const wfpCountries = new Set((scores ?? []).map((s) => s.countryiso3))

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Legend */}
      <div className="flex items-center gap-4 px-4 py-2 bg-white border-b border-gray-200 text-xs text-gray-600 shrink-0">
        <span className="font-medium">Crisis Score:</span>
        {[
          { colour: '#16a34a', label: 'Stable (0–25)' },
          { colour: '#ca8a04', label: 'Moderate (25–50)' },
          { colour: '#ea580c', label: 'High (50–75)' },
          { colour: '#dc2626', label: 'Critical (75–100)' },
          { colour: '#d1d5db', label: 'No data' },
        ].map(({ colour, label }) => (
          <span key={label} className="flex items-center gap-1">
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ backgroundColor: colour }}
            />
            {label}
          </span>
        ))}
        {loading && <span className="ml-auto text-gray-400">Loading scores…</span>}
        {error && <span className="ml-auto text-red-500">Failed to load scores</span>}
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Map */}
        <div className="flex-1 relative">
          <ChoroplethMap
            scores={scores ?? []}
            onCountryClick={setSelectedIso3}
            selectedIso3={selectedIso3}
          />
        </div>

        {/* Detail panel — only for WFP countries */}
        {selectedIso3 && wfpCountries.has(selectedIso3) && (
          <CountryDetailPanel
            iso3={selectedIso3}
            onClose={() => setSelectedIso3(null)}
          />
        )}
      </div>
    </div>
  )
}
