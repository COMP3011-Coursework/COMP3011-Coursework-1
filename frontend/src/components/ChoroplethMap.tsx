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
  const containerRef = useRef<HTMLDivElement>(null)

  const scoreMap = new Map(scores.map((s) => [s.countryiso3, s]))

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

  // Update GeoJSON layer when scores load
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    fetch('/data/world.geojson')
      .then((r) => r.json())
      .then((geoData) => {
        if (geoLayerRef.current) {
          geoLayerRef.current.remove()
        }

        const layer = L.geoJSON(geoData, {
          style: (feature) => {
            const iso3 = feature?.properties?.ISO_A3 as string
            const s = scoreMap.get(iso3)
            return {
              fillColor: crisisColour(s?.crisis_score),
              fillOpacity: iso3 === selectedIso3 ? 0.95 : 0.7,
              color: iso3 === selectedIso3 ? '#1d4ed8' : '#6b7280',
              weight: iso3 === selectedIso3 ? 2 : 0.5,
            }
          },
          onEachFeature: (feature, featureLayer) => {
            const iso3 = feature?.properties?.ISO_A3 as string
            const s = scoreMap.get(iso3)
            if (s) {
              featureLayer.bindTooltip(
                `<strong>${iso3}</strong><br/>Score: ${s.crisis_score.toFixed(1)} (${s.severity})`,
                { sticky: true, className: 'text-xs' },
              )
            }
            featureLayer.on('click', () => onCountryClick(iso3))
            featureLayer.on('mouseover', function (this: L.Path) {
              this.setStyle({ fillOpacity: 0.9 })
            })
            featureLayer.on('mouseout', function (this: L.Path) {
              this.setStyle({ fillOpacity: iso3 === selectedIso3 ? 0.95 : 0.7 })
            })
          },
        })

        layer.addTo(map)
        geoLayerRef.current = layer
      })
      .catch(console.error)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scores, selectedIso3])

  return <div ref={containerRef} className="w-full h-full" />
}
