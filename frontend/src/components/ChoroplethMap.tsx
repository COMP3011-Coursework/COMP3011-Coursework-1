import L from 'leaflet'
import { useEffect, useRef } from 'react'
import type { CrisisScore } from '../types'

interface Props {
  scores: CrisisScore[]
  onCountryClick: (iso3: string) => void
  selectedIso3?: string | null
}

function crisisColour(score?: number): string {
  if (score === undefined) return '#d1d5db'
  if (score >= 75) return '#dc2626'
  if (score >= 50) return '#ea580c'
  if (score >= 25) return '#ca8a04'
  return '#16a34a'
}

export default function ChoroplethMap({ scores, onCountryClick, selectedIso3 }: Props) {
  const mapRef = useRef<L.Map | null>(null)
  const geoLayerRef = useRef<L.GeoJSON | null>(null)
  const featureLayersRef = useRef<Map<string, L.Path>>(new Map())
  const containerRef = useRef<HTMLDivElement>(null)
  const prevSelectedRef = useRef<string | null | undefined>(null)

  // Initialise map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = L.map(containerRef.current, { zoomControl: true }).setView([20, 10], 2)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      maxZoom: 19,
    }).addTo(map)
    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  // Rebuild GeoJSON layer only when scores change
  useEffect(() => {
    const scoreMap = new Map(scores.map((s) => [s.countryiso3, s]))
    const controller = new AbortController()

    fetch('/data/world.geojson', { signal: controller.signal })
      .then((r) => r.json())
      .then((geoData) => {
        if (controller.signal.aborted) return
        const map = mapRef.current
        if (!map) return
        if (geoLayerRef.current) {
          geoLayerRef.current.remove()
        }
        featureLayersRef.current.clear()

        const layer = L.geoJSON(geoData, {
          style: (feature) => {
            const iso3 = (feature?.properties?.['ISO3166-1-Alpha-3'] ?? feature?.properties?.ISO_A3) as string
            const invalid = !iso3 || iso3.startsWith('-')
            const s = invalid ? undefined : scoreMap.get(iso3)
            return {
              fillColor: crisisColour(s?.crisis_score),
              fillOpacity: 0.7,
              color: '#6b7280',
              weight: 0.5,
            }
          },
          onEachFeature: (feature, featureLayer) => {
            const iso3 = (feature?.properties?.['ISO3166-1-Alpha-3'] ?? feature?.properties?.ISO_A3) as string
            if (!iso3 || iso3 === '-99' || iso3 === '-' || iso3.startsWith('-')) return
            const s = scoreMap.get(iso3)
            featureLayersRef.current.set(iso3, featureLayer as L.Path)
            if (s) {
              featureLayer.bindTooltip(
                `<strong>${iso3}</strong><br/>Score: ${s.crisis_score.toFixed(1)} (${s.severity})`,
                { sticky: true, className: 'text-xs' },
              )
              featureLayer.on('click', () => onCountryClick(iso3))
            } else {
              featureLayer.bindTooltip(
                `<strong>${iso3}</strong><br/>No WFP food price data for this country/region`,
                { sticky: true, className: 'text-xs' },
              )
            }
            featureLayer.on('mouseover', function (this: L.Path) {
              this.setStyle({ fillOpacity: 0.9 })
            })
            featureLayer.on('mouseout', function (this: L.Path) {
              const isSelected = iso3 === prevSelectedRef.current
              this.setStyle({ fillOpacity: isSelected ? 0.95 : 0.7 })
            })
          },
        })

        layer.addTo(map)
        geoLayerRef.current = layer
      })
      .catch((err) => { if (err.name !== 'AbortError') console.error(err) })

    return () => controller.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scores])

  // Update selected country styling without rebuilding the layer
  useEffect(() => {
    const prev = prevSelectedRef.current
    prevSelectedRef.current = selectedIso3 ?? null

    if (prev) {
      featureLayersRef.current.get(prev)?.setStyle({
        fillOpacity: 0.7,
        color: '#6b7280',
        weight: 0.5,
      })
    }
    if (selectedIso3) {
      featureLayersRef.current.get(selectedIso3)?.setStyle({
        fillOpacity: 0.95,
        color: '#1d4ed8',
        weight: 2,
      })
    }
  }, [selectedIso3])

  return <div ref={containerRef} className="w-full h-full" />
}
